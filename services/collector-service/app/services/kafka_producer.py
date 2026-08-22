from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from aiokafka import AIOKafkaProducer
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = structlog.get_logger()

_BASE_TOPICS = {
    "events",
    "alerts",
    "incidents",
    "threat_intel",
    "audit_logs",
    "response_actions",
    "metrics",
}


class KafkaProducerService:
    """Async Kafka producer that publishes events to topics."""

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=self._serialize,
            key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
            acks="all",
            enable_idempotence=True,
            max_in_flight_requests_per_connection=5,
            retries=3,
        )
        await self._producer.start()
        logger.info(
            "kafka_producer_started",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        )

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            logger.info("kafka_producer_stopped")

    @staticmethod
    def _serialize(value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        return json.dumps(value, default=str, ensure_ascii=False).encode("utf-8")

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=5),
        reraise=True,
    )
    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        key: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        if self._producer is None:
            raise RuntimeError("KafkaProducerService is not started. Call start() first.")

        message_id = str(uuid.uuid4())
        enriched = {
            "message_id": message_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "topic": topic,
            **payload,
        }

        kafka_headers = [(k.encode("utf-8"), v.encode("utf-8")) for k, v in (headers or {}).items()]

        partition_key = key or message_id

        record_metadata = await self._producer.send_and_wait(
            topic=topic,
            value=enriched,
            key=partition_key,
            headers=kafka_headers or None,
        )

        logger.info(
            "event_published",
            topic=topic,
            partition=record_metadata.partition,
            offset=record_metadata.offset,
            message_id=message_id,
        )

    async def publish_event(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("events", payload, key=key)

    async def publish_alert(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("alerts", payload, key=key)

    async def publish_incident(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("incidents", payload, key=key)

    async def publish_threat_intel(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("threat_intel", payload, key=key)

    async def publish_audit_log(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("audit_logs", payload, key=key)

    async def publish_response_action(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("response_actions", payload, key=key)

    async def publish_metric(self, payload: dict[str, Any], key: str | None = None) -> None:
        await self.publish("metrics", payload, key=key)


kafka_producer = KafkaProducerService()
