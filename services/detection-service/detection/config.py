from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "detection-service"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"

    KAFKA_TOPIC_SECURITY_EVENTS: str = "security-events"
    KAFKA_TOPIC_ALERTS: str = "alerts"
    KAFKA_TOPIC_INCIDENTS: str = "incidents"
    KAFKA_TOPIC_DEAD_LETTER: str = "dead-letter-queue"

    KAFKA_CONSUMER_GROUP: str = "detection-engine"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"

    BRUTE_FORCE_THRESHOLD: int = 5
    BRUTE_FORCE_WINDOW_SECONDS: int = 300

    PORT_SCAN_THRESHOLD: int = 20
    PORT_SCAN_WINDOW_SECONDS: int = 60

    UNUSUAL_LOGIN_START_HOUR: int = 22
    UNUSUAL_LOGIN_END_HOUR: int = 6

    INCIDENT_EXPIRY_SECONDS: int = 3600
    INCIDENT_MAX_EVENTS: int = 200

    SIGMA_RULES_PATH: str = "detection-rules/sigma"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
