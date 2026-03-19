import uuid
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier. Auto-generated if not provided.",
    )
    message: str = Field(..., min_length=1, max_length=10_000)
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt to steer Claude's behaviour.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "abc-123",
                    "message": "What is the capital of France?",
                    "system_prompt": "You are a helpful geography tutor.",
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    turn: int
    input_tokens: int
    output_tokens: int


class SessionInfo(BaseModel):
    session_id: str
    turn_count: int
    message: str = "Session cleared"