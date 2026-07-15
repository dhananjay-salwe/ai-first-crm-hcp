import os
import time
import json
from typing import TypedDict, Sequence, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError
from langgraph.graph import StateGraph, END
from schema import InteractionState

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured. Set it in your .env file.")

# timeout / max_retries guard against Groq being slow or transiently
# unavailable, which used to surface as an unhandled exception -> 500.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,  # low temp, we want consistent extraction not creativity
    groq_api_key=GROQ_API_KEY,
    timeout=30,
    max_retries=2,
)


class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    structured_data: InteractionState


SYSTEM_PROMPT = """You are an AI Assistant for a Life Sciences CRM. Your job is to manage HCP interactions.
Analyze the user's input and determine which tool action is required.

Available Operations:
1. Log Interaction: Extract all relevant details (HCP Name, Topics, Materials, Sentiment, Outcomes).
2. Edit Interaction: Update specific fields of an existing log based on user corrections.
3. Suggest Follow-ups: Create actionable tasks.
4. Fetch History: Retrieve past notes (Mocked).
5. Analyze Sentiment: Explicitly flag as Positive, Neutral, or Negative.

You will be shown the form's current values right before the user's message - treat
that as what's already logged. Only change a field if the user's latest message
actually gives you new information about it. If a field isn't mentioned, carry its
existing value forward exactly as given - don't reset it back to a default."""

_MAX_ATTEMPTS = 3


def call_model(state: AgentState):
    # Feed the current state in as its own system message so the model has
    # something concrete to diff against, instead of extracting from the
    # user's text in a vacuum every single turn.
    current_state_msg = SystemMessage(
        content=f"Current form values: {state['structured_data'].model_dump_json()}"
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT), current_state_msg] + list(state["messages"])
    structured_llm = llm.with_structured_output(InteractionState)

    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = structured_llm.invoke(messages)
            return {"structured_data": response}
        except (OutputParserException, ValidationError) as exc:
            last_error = exc
        except Exception as exc:
            # groq's SDK errors (rate limit, timeout, connection) all just
            # inherit from Exception, not worth importing their types here
            last_error = exc

        if attempt < _MAX_ATTEMPTS:
            time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(
        f"LLM failed to produce valid structured output after {_MAX_ATTEMPTS} attempts: {last_error}"
    )


workflow = StateGraph(AgentState)
workflow.add_node("agent_processor", call_model)
workflow.set_entry_point("agent_processor")
workflow.add_edge("agent_processor", END)
app_graph = workflow.compile()


if __name__ == "__main__":
    test_input = (
        "Met Dr. Smith today at 3 PM. We discussed the efficacy of Product X. "
        "She was thrilled about the Phase III trial data and wants an OncoBoost "
        "brochure sent over. I gave her 2 sample kits."
    )

    inputs = {
        "messages": [HumanMessage(content=test_input)],
        "structured_data": InteractionState(),
    }

    print("Running initial agent text analysis test...\n")
    result = app_graph.invoke(inputs)
    print(json.dumps(result["structured_data"].model_dump(), indent=4))