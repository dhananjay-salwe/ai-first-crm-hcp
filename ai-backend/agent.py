import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from schema import InteractionState

load_dotenv()

# Initialize the mandatory Groq model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1, # Low temperature for accurate entity extraction
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Define the state that passes through our graph
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    structured_data: InteractionState

# --- System Prompt telling the AI how to behave like an HCP CRM Assistant ---
SYSTEM_PROMPT = """You are an AI Assistant for a Life Sciences CRM. Your job is to manage HCP interactions.
Analyze the user's input and determine which tool action is required. 

Available Operations:
1. Log Interaction: Extract all relevant details (HCP Name, Topics, Materials, Sentiment, Outcomes).
2. Edit Interaction: Update specific fields of an existing log based on user corrections.
3. Suggest Follow-ups: Create actionable tasks.
4. Fetch History: Retrieve past notes (Mocked).
5. Analyze Sentiment: Explicitly flag as Positive, Neutral, or Negative.

You must respond by structuring your understanding cleanly."""

def call_model(state: AgentState):
    messages = [AIMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
    
    # We force the LLM to output structured data matching our UI goals
    structured_llm = llm.with_structured_output(InteractionState)
    response = structured_llm.invoke(messages)
    
    return {"structured_data": response}

# Define the LangGraph workflow
workflow = StateGraph(AgentState)

# Add our processing node
workflow.add_node("agent_processor", call_model)

# Set the entry point and end target
workflow.set_entry_point("agent_processor")
workflow.add_edge("agent_processor", END)

# Compile the graph
app_graph = workflow.compile()

# --- Fast Local Test Execution Block ---
if __name__ == "__main__":
    test_input = "Met Dr. Smith today at 3 PM. We discussed the efficacy of Product X. She was thrilled about the Phase III trial data and wants an OncoBoost brochure sent over. I gave her 2 sample kits."
    
    inputs = {
        "messages": [HumanMessage(content=test_input)],
        "structured_data": InteractionState()
    }
    
    print("Running initial agent text analysis test...\n")
    result = app_graph.invoke(inputs)
    
    import json
    print(json.dumps(result["structured_data"].dict(), indent=4))