from typing import Literal
from pydantic import BaseModel


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationHistory(BaseModel):
    session_id: str
    turns: list[Turn] = []

    def to_claude_messages(self) -> list[dict]:
        return [{"role": t.role, "content": t.content} for t in self.turns]

    @property
    def turn_count(self) -> int:
        """Number of complete user/assistant exchanges."""
        return len(self.turns) // 2