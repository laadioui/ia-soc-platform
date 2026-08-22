from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI SOC Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite+aiosqlite:///./soc_platform.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    OPENSEARCH_URL: str = "http://localhost:9200"

    JWT_SECRET_KEY: str = "changeme_jwt_secret_key_2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5

    SOAR_SIMULATION_MODE: bool = True

    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SLACK_WEBHOOK_URL: str = ""
    DISCORD_WEBHOOK_URL: str = ""

    POSTGRES_USER: str = "soc_admin"
    POSTGRES_PASSWORD: str = "soc_secret_password_2026"
    POSTGRES_DB: str = "ai_soc_platform"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "ai-soc"
    KEYCLOAK_CLIENT_ID: str = "soc-frontend"
    KEYCLOAK_CLIENT_SECRET: str = ""

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
