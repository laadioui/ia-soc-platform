# Optional infrastructure integrations (Kafka, OpenSearch, Redis) are not part
# of the base requirements: importing app.services must stay safe without them
# (e.g. on minimal deployments where only demo_seed is used).
from typing import Any

_optional: dict[str, Any] = {}

for _module, _name in (
    ("app.services.kafka_producer", "KafkaProducerService"),
    ("app.services.opensearch_client", "OpenSearchClient"),
    ("app.services.redis_client", "RedisClient"),
):
    try:
        _optional[_name] = getattr(__import__(_module, fromlist=[_name]), _name)
    except Exception:  # pragma: no cover - depends on optional extras
        _optional[_name] = None

KafkaProducerService = _optional["KafkaProducerService"]
OpenSearchClient = _optional["OpenSearchClient"]
RedisClient = _optional["RedisClient"]

__all__ = ["KafkaProducerService", "OpenSearchClient", "RedisClient"]
