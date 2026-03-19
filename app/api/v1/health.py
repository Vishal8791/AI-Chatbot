from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def health():
    s = get_settings()
    return {
        "status": "ok",
        # "model": s.claude_model,
        "model": s.gemini_model,
        "memory_backend": s.memory_backend,
    }