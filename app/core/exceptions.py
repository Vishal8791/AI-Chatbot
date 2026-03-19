from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class SessionNotFoundError(Exception):
    pass


class ClaudeAPIError(Exception):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SessionNotFoundError)
    async def session_not_found(_req: Request, exc: SessionNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found", "detail": str(exc)},
        )

    @app.exception_handler(ClaudeAPIError)
    async def claude_api_error(_req: Request, exc: ClaudeAPIError):
        return JSONResponse(
            status_code=502,
            content={"error": "Upstream AI service error", "detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def value_error(_req: Request, exc: ValueError):
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "detail": str(exc)},
        )