import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional

from schema import InteractionState
from agent import app_graph
from langchain_core.messages import HumanMessage
from langchain_core.exceptions import OutputParserException
from database import SessionLocal, InteractionRecord

app = FastAPI(title="AI-First CRM HCP Backend")

# In production, restrict this to your actual React app URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    current_form_state: Optional[Dict[str, Any]] = None


class SaveRequest(BaseModel):
    data: InteractionState


# --- The 5 Agent Tools ---

def tool_log_interaction(data: InteractionState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        new_record = InteractionRecord(
            hcp_name=data.hcp_name,
            interaction_data=data.model_dump(),
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "success", "id": new_record.id, "message": "Interaction logged to MySQL."}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def tool_edit_interaction(record_id: int, updated_data: InteractionState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        record = db.query(InteractionRecord).filter(InteractionRecord.id == record_id).first()
        if not record:
            return {"status": "error", "message": "Record not found."}

        record.hcp_name = updated_data.hcp_name
        record.interaction_data = updated_data.model_dump()
        db.commit()
        return {"status": "success", "id": record_id, "message": "MySQL Interaction updated."}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def tool_analyze_sentiment(sentiment: str) -> str:
    valid_sentiments = ["Positive", "Neutral", "Negative"]
    return sentiment if sentiment in valid_sentiments else "Neutral"


def tool_suggest_followups(topics: str, sentiment: str) -> List[str]:
    suggestions = []
    if "efficacy" in topics.lower() or "trial" in topics.lower():
        suggestions.append("Schedule follow-up meeting in 2 weeks")
        suggestions.append("Send OncoBoost Phase III PDF")
    if sentiment == "Positive":
        suggestions.append("Add doctor to the regional advisory board invite list")
    return suggestions


def tool_fetch_hcp_history(hcp_name: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        records = db.query(InteractionRecord).filter(InteractionRecord.hcp_name == hcp_name).all()
        return [{"id": record.id, "data": record.interaction_data} for record in records]
    finally:
        db.close()


# --- API Endpoints ---

@app.post("/api/chat")
async def handle_agent_chat(request: ChatRequest):
    """
    Main chat endpoint. Takes the raw text plus whatever the form already
    has, runs it through the agent, and hands back the merged/updated fields.
    """
    # Whatever the frontend has on screen becomes the agent's starting
    # point, so a follow-up message doesn't wipe out fields we already got
    # right. If the payload is malformed for some reason, fall back to a
    # blank state rather than failing the whole request over it.
    try:
        prior_state = InteractionState(**(request.current_form_state or {}))
    except ValidationError:
        prior_state = InteractionState()

    try:
        inputs = {
            "messages": [HumanMessage(content=request.message)],
            "structured_data": prior_state,
        }
        graph_output = app_graph.invoke(inputs)
        extracted_fields: InteractionState = graph_output["structured_data"]
    except (OutputParserException, ValidationError) as e:
        raise HTTPException(status_code=502, detail=f"AI returned invalid structured data: {e}")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI processing failed: {e}")

    extracted_fields.sentiment = tool_analyze_sentiment(extracted_fields.sentiment)

    if extracted_fields.topics_discussed:
        extracted_fields.ai_suggested_followups = tool_suggest_followups(
            extracted_fields.topics_discussed,
            extracted_fields.sentiment,
        )

    # A DB failure here shouldn't get swallowed - the frontend previously
    # could show a "success" reply while nothing was actually saved. We
    # still return the extracted data either way (the AI work isn't lost),
    # but the save outcome gets surfaced so the UI can warn the user.
    try:
        db_status = tool_log_interaction(extracted_fields)
    except Exception as e:
        db_status = {"status": "error", "message": f"Could not save interaction to MySQL: {e}"}

    return {
        "reply": f"I've analyzed that for you. I recognized the interaction details with {extracted_fields.hcp_name or 'the HCP'}.",
        "extracted_data": extracted_fields.model_dump(),
        "database": db_status,
    }


@app.post("/api/save")
async def save_interaction(request: SaveRequest):
    """Manual save - used when the user hits 'Log' with the form as-is, no AI parsing involved."""
    try:
        return tool_log_interaction(request.data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not save interaction: {e}")


@app.put("/api/edit/{record_id}")
async def edit_interaction(record_id: int, request: SaveRequest):
    try:
        return tool_edit_interaction(record_id, request.data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not update interaction: {e}")


@app.get("/api/history/{hcp_name}")
async def get_hcp_history(hcp_name: str):
    try:
        return {"hcp_name": hcp_name, "history": tool_fetch_hcp_history(hcp_name)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not fetch history: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)