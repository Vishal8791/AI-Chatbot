"""
Dependency injection wiring.
To swap implementations (e.g. Redis repo, different LLM client),
change only this file — services remain untouched.
"""
from functools import lru_cache

from fastapi import Depends

from app.repositories.conversation_repo import (
    ConversationRepository,
    InMemoryConversationRepository,
)
from app.services.chat_service import ChatService
from app.services.claude_client import ClaudeClient
from app.services.memory_service import MemoryService


@lru_cache
def get_claude_client() -> ClaudeClient:
    return ClaudeClient()


@lru_cache
def get_repo() -> ConversationRepository:
    # Swap for RedisConversationRepository(get_settings().redis_url) in production
    return InMemoryConversationRepository()


def get_memory_service(
    repo: ConversationRepository = Depends(get_repo),
) -> MemoryService:
    return MemoryService(repo)


def get_chat_service(
    claude: ClaudeClient = Depends(get_claude_client),
    memory: MemoryService = Depends(get_memory_service),
) -> ChatService:
    return ChatService(claude, memory)