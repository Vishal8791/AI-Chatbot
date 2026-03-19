import time
import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI, settings) -> None:
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID + timing
    @app.middleware("http")
    async def request_id_and_timing(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms:.1f}ms"

        logger.info(
            "method=%s path=%s status=%d request_id=%s time=%.1fms",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
            elapsed_ms,
        )
        return response