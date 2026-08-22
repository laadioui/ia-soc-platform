from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI SOC AI-Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql+asyncpg://soc_admin:soc_secret_password_2026@localhost:5432/ai_soc_platform"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    REDIS_URL: str = "redis://localhost:6379/0"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
