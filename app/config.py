from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = "placeholder"
    gemini_model: str = "gemini-3.1-flash-lite-preview"
    max_tokens: int = 2048

    
    # Anthropic
    # anthropic_api_key: str = "sk-ant-placeholder"
    # claude_model: str = "claude-opus-4-20250514"
    # max_tokens: int = 2048

    # Memory
    memory_backend: str = "memory"       # "memory" | "redis"
    redis_url: str = "redis://localhost:6379"
    max_history_turns: int = 20

    # Server
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()