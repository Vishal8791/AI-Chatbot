from abc import ABC, abstractmethod
from app.models.memory import ConversationHistory


# ── Abstract base ────────────────────────────────────────────────────────────

class ConversationRepository(ABC):
    @abstractmethod
    async def get(self, session_id: str) -> ConversationHistory | None: ...

    @abstractmethod
    async def save(self, history: ConversationHistory) -> None: ...

    @abstractmethod
    async def delete(self, session_id: str) -> None: ...


# ── In-memory implementation (default / dev / testing) ───────────────────────

class InMemoryConversationRepository(ConversationRepository):
    def __init__(self) -> None:
        self._store: dict[str, ConversationHistory] = {}

    async def get(self, session_id: str) -> ConversationHistory | None:
        return self._store.get(session_id)

    async def save(self, history: ConversationHistory) -> None:
        self._store[history.session_id] = history

    async def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)


# ── Redis implementation (production) ────────────────────────────────────────
# Uncomment and install redis to enable.
#
# import json
# import redis.asyncio as aioredis
#
# class RedisConversationRepository(ConversationRepository):
#     def __init__(self, redis_url: str, ttl_seconds: int = 86_400) -> None:
#         self._redis = aioredis.from_url(redis_url, decode_responses=True)
#         self._ttl = ttl_seconds
#
#     async def get(self, session_id: str) -> ConversationHistory | None:
#         raw = await self._redis.get(f"chat:{session_id}")
#         if raw is None:
#             return None
#         return ConversationHistory.model_validate_json(raw)
#
#     async def save(self, history: ConversationHistory) -> None:
#         await self._redis.set(
#             f"chat:{history.session_id}",
#             history.model_dump_json(),
#             ex=self._ttl,
#         )
#
#     async def delete(self, session_id: str) -> None:
#         await self._redis.delete(f"chat:{session_id}")