from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any


class InteractionState(BaseModel):
    hcp_name: Optional[str] = Field(None, description="Name of the Healthcare Professional/Doctor")
    interaction_type: str = Field("Meeting", description="Type of interaction, e.g., Meeting, Call, Email")
    date: Optional[str] = Field(None, description="Date of the interaction (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Time of the interaction (HH:MM)")
    attendees: List[str] = Field(default_factory=list, description="Array of strings for people present")
    topics_discussed: Optional[str] = Field(None, description="Summary of key discussion points")
    materials_shared: List[str] = Field(default_factory=list, description="Materials shared with the doctor")
    samples_distributed: List[str] = Field(default_factory=list, description="Samples distributed to the doctor")
    sentiment: str = Field("Neutral", description="Inferred sentiment: Positive, Neutral, or Negative")
    outcomes: Optional[str] = Field(None, description="Key outcomes or agreements reached")
    follow_up_actions: Optional[str] = Field(None, description="Next steps or tasks derived from the conversation")
    ai_suggested_followups: List[str] = Field(
        default_factory=list, description="Array of strings for AI generated system follow-up tasks"
    )

    # Groq's structured output is usually fine but not perfect - sometimes we
    # get a comma separated string back instead of an actual list, sometimes
    # a field just comes back null. Clean it up here instead of letting
    # pydantic throw and turn it into a 500 on /api/chat.
    @field_validator(
        "attendees", "ai_suggested_followups", "materials_shared", "samples_distributed",
        mode="before",
    )
    @classmethod
    def _coerce_to_list(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("interaction_type", mode="before")
    @classmethod
    def _default_interaction_type(cls, value: Any) -> str:
        return value or "Meeting"

    @field_validator("sentiment", mode="before")
    @classmethod
    def _validate_sentiment(cls, value: Any) -> str:
        valid = {"Positive", "Neutral", "Negative"}
        return value if value in valid else "Neutral"