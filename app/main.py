"""
Entry point for the AI Chatbot API.
Run with:  uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import register_middleware

settings = get_settings()
setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    import logging
    logging.getLogger(__name__).info(
        # "startup model=%s memory=%s", settings.claude_model, settings.memory_backend
        "startup model=%s memory=%s", settings.gemini_model, settings.memory_backend
    )
    yield
    logging.getLogger(__name__).info("shutdown")


app = FastAPI(
    title="AI Chatbot API",
    description="Production-ready chatbot powered by Gemini with conversation memory.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

register_middleware(app, settings)
register_exception_handlers(app)
app.include_router(api_router, prefix="/api")

# Serve frontend
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def root():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "AI Chatbot API", "docs": "/docs", "health": "/api/v1/health"}