from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI SOC Notification-Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "notification-service"
    KAFKA_TOPICS: list[str] = ["incidents", "alerts"]

    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "soc-alerts@example.com"
    SMTP_FROM_NAME: str = "SOC Platform"

    SLACK_WEBHOOK_URL: str = ""
    DISCORD_WEBHOOK_URL: str = ""
    CUSTOM_WEBHOOK_URLS: list[str] = []

    NOTIFICATION_EMAIL_RECIPIENTS: list[str] = []
    MIN_SEVERITY_FOR_EMAIL: str = "high"
    MIN_SEVERITY_FOR_WEBHOOK: str = "medium"

    REDIS_URL: str = "redis://localhost:6379/0"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8002

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
