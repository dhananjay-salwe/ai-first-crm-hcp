from pydantic import BaseModel, Field
from typing import List, Optional

class InteractionState(BaseModel):
    hcp_name: Optional[str] = Field(None, description="Name of the Healthcare Professional/Doctor")
    interaction_type: str = Field("Meeting", description="Type of interaction, e.g., Meeting, Call, Email")
    date: Optional[str] = Field(None, description="Date of the interaction (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Time of the interaction (HH:MM)")
    attendees: List[str] = Field(default_factory=list, description="Array of strings for people present")
    topics_discussed: Optional[str] = Field(None, description="Summary of key discussion points")
    materials_shared: List[str] = Field(default_factory=list, description="MUST be an array of strings. Example: ['OncoBoost brochure']")
    samples_distributed: List[str] = Field(default_factory=list, description="MUST be an array of strings. Example: ['2 sample kits']")
    sentiment: str = Field("Neutral", description="Inferred sentiment: Positive, Neutral, or Negative")
    outcomes: Optional[str] = Field(None, description="Key outcomes or agreements reached")
    follow_up_actions: Optional[str] = Field(None, description="Next steps or tasks derived from the conversation")
    ai_suggested_followups: List[str] = Field(default_factory=list, description="Array of strings for AI generated system follow-up tasks")