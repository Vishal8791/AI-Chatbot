import logging

from app.models.chat import ChatRequest, ChatResponse
from app.services.claude_client import ClaudeClient
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestrates memory retrieval, Claude completion, and history persistence."""

    def __init__(self, claude: ClaudeClient, memory: MemoryService) -> None:
        self._claude = claude
        self._memory = memory

    async def handle(self, req: ChatRequest) -> ChatResponse:
        logger.info("session=%s | handling message len=%d", req.session_id, len(req.message))

        history = await self._memory.get_history(req.session_id)

        # Build message list: history + new user turn
        messages = history.to_claude_messages()
        messages.append({"role": "user", "content": req.message})

        reply, in_tok, out_tok = await self._claude.complete(
            messages=messages,
            system=req.system_prompt,
        )

        await self._memory.append(req.session_id, req.message, reply)

        logger.info(
            "session=%s | done turn=%d in_tokens=%d out_tokens=%d",
            req.session_id,
            history.turn_count + 1,
            in_tok,
            out_tok,
        )

        return ChatResponse(
            session_id=req.session_id,
            reply=reply,
            turn=history.turn_count + 1,
            input_tokens=in_tok,
            output_tokens=out_tok,
        )

    async def clear_session(self, session_id: str) -> None:
        await self._memory.clear(session_id)