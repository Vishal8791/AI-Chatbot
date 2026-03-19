import logging

from fastapi import APIRouter, Depends

from app.dependencies import get_chat_service
from app.models.chat import ChatRequest, ChatResponse, SessionInfo
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send a message",
    description=(
        "Send a message and receive a reply from Claude. "
        "Pass the same `session_id` across requests to maintain conversation history."
    ),
)
async def send_message(
    body: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await service.handle(body)


@router.get(
    "/{session_id}/history",
    summary="Get session info",
    description="Returns turn count for a session (does not expose message content).",
)
async def get_session_info(
    session_id: str,
    service: ChatService = Depends(get_chat_service),
) -> dict:
    history = await service._memory.get_history(session_id)
    return {"session_id": session_id, "turn_count": history.turn_count}


@router.delete(
    "/{session_id}",
    response_model=SessionInfo,
    summary="Clear session history",
)
async def clear_session(
    session_id: str,
    service: ChatService = Depends(get_chat_service),
) -> SessionInfo:
    history = await service._memory.get_history(session_id)
    turn_count = history.turn_count
    await service.clear_session(session_id)
    return SessionInfo(session_id=session_id, turn_count=turn_count)