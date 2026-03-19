import logging

from app.config import get_settings
from app.models.memory import ConversationHistory, Turn
from app.repositories.conversation_repo import ConversationRepository

logger = logging.getLogger(__name__)


class MemoryService:
    """Manages per-session conversation history with a sliding-window cap."""

    def __init__(self, repo: ConversationRepository) -> None:
        self._repo = repo
        self._max_turns = get_settings().max_history_turns

    async def get_history(self, session_id: str) -> ConversationHistory:
        return await self._repo.get(session_id) or ConversationHistory(session_id=session_id)

    async def append(
        self,
        session_id: str,
        user_msg: str,
        assistant_reply: str,
    ) -> None:
        history = await self.get_history(session_id)
        history.turns.append(Turn(role="user", content=user_msg))
        history.turns.append(Turn(role="assistant", content=assistant_reply))

        # Sliding window — keep only the most recent N exchanges
        max_raw = self._max_turns * 2
        if len(history.turns) > max_raw:
            history.turns = history.turns[-max_raw:]
            logger.debug("session=%s | trimmed history to %d turns", session_id, self._max_turns)

        await self._repo.save(history)

    async def clear(self, session_id: str) -> None:
        await self._repo.delete(session_id)
        logger.info("session=%s | history cleared", session_id)