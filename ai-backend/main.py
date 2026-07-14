import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import our schema and agent graph
from schema import InteractionState
from agent import app_graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="AI-First CRM HCP Backend")

# Enable CORS so your React frontend can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Database to store interaction records locally for testing
db_storage: Dict[int, Dict[str, Any]] = {}
id_counter = 1

# --- API Request Models ---
class ChatRequest(BaseModel):
    message: str
    current_form_state: Optional[Dict[str, Any]] = None

class SaveRequest(BaseModel):
    data: InteractionState

# --- The 5 Agent Tools (Exposed as Backend Capabilities) ---

def tool_log_interaction(data: InteractionState) -> Dict[str, Any]:
    """Tool 1 (Mandatory): Saves the extracted interaction data into the database."""
    global id_counter
    record_id = id_counter
    db_storage[record_id] = data.dict()
    id_counter += 1
    return {"status": "success", "id": record_id, "message": "Interaction successfully logged."}

def tool_edit_interaction(record_id: int, updated_data: InteractionState) -> Dict[str, Any]:
    """Tool 2 (Mandatory): Modifies an existing logged interaction."""
    if record_id not in db_storage:
        return {"status": "error", "message": "Record not found."}
    db_storage[record_id] = updated_data.dict()
    return {"status": "success", "id": record_id, "message": "Interaction successfully updated."}

def tool_analyze_sentiment(sentiment: str) -> str:
    """Tool 3: Maps and validates the doctor's sentiment profile."""
    valid_sentiments = ["Positive", "Neutral", "Negative"]
    return sentiment if sentiment in valid_sentiments else "Neutral"

def tool_suggest_followups(topics: str, sentiment: str) -> List[str]:
    """Tool 4: Generates proactive sales next-steps based on discussion context."""
    suggestions = []
    if "efficacy" in topics.lower() or "trial" in topics.lower():
        suggestions.append("Schedule follow-up meeting in 2 weeks")
        suggestions.append("Send OncoBoost Phase III PDF")
    if sentiment == "Positive":
        suggestions.append("Add doctor to the regional advisory board invite list")
    return suggestions

def tool_fetch_hcp_history(hcp_name: str) -> List[Dict[str, Any]]:
    """Tool 5: Historical lookup tool to track previous touches with this doctor."""
    history = []
    for rid, record in db_storage.items():
        if record.get("hcp_name") == hcp_name:
            history.append({"id": rid, "date": record.get("date"), "topics": record.get("topics_discussed")})
    return history


# --- API Endpoints ---

@app.post("/api/chat")
async def handle_agent_chat(request: ChatRequest):
    """
    Main Chat Interface Endpoint. Processes messy text, executes the LangGraph node,
    runs the specialized tools, and sends structured field data back to React.
    """
    try:
        # Run user text through the LangGraph configuration
        inputs = {
            "messages": [HumanMessage(content=request.message)],
            "structured_data": InteractionState()
        }
        
        graph_output = app_graph.invoke(inputs)
        extracted_fields: InteractionState = graph_output["structured_data"]
        
        # Run Tool 3: Sentiment Processing
        extracted_fields.sentiment = tool_analyze_sentiment(extracted_fields.sentiment)
        
        # Run Tool 4: Dynamic Follow-up Suggestions
        if extracted_fields.topics_discussed:
            extracted_fields.ai_suggested_followups = tool_suggest_followups(
                extracted_fields.topics_discussed, 
                extracted_fields.sentiment
            )
            
        return {
            "reply": f"I've analyzed that for you. I recognized the interaction details with {extracted_fields.hcp_name or 'the HCP'}.",
            "extracted_data": extracted_fields.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save")
async def save_interaction(request: SaveRequest):
    """Endpoint for when the user hits the manual 'Log' button on the form UI."""
    result = tool_log_interaction(request.data)
    return result

@app.put("/api/edit/{record_id}")
async def edit_interaction(record_id: int, request: SaveRequest):
    """Endpoint to update an existing database record explicitly."""
    result = tool_edit_interaction(record_id, request.data)
    return result

@app.get("/api/history/{hcp_name}")
async def get_hcp_history(hcp_name: str):
    """Endpoint to trigger historical insights tool for a specific doctor."""
    return {"hcp_name": hcp_name, "history": tool_fetch_hcp_history(hcp_name)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)