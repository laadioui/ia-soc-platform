from __future__ import annotations

import asyncio
import signal
from typing import Any

import structlog
from aiokafka import AIOKafkaConsumer
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.notifiers.email import email_notifier
from app.notifiers.webhook import webhook_notifier

logger = structlog.get_logger()

_consumer: AIOKafkaConsumer | None = None
_shutdown_event = asyncio.Event()


def _setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


async def _process_message(message_value: dict[str, Any], topic: str) -> None:
    logger.info(
        "processing_message",
        topic=topic,
        partition=message_value.get("partition"),
        offset=message_value.get("offset"),
    )

    payload = message_value.get("value", {})
    if not payload:
        logger.warning("empty_message_payload", topic=topic)
        return

    payload.setdefault("topic_source", topic)

    results: dict[str, Any] = {}

    email_result = await email_notifier.send_notification(payload)
    results["email"] = email_result

    webhook_results = await webhook_notifier.send_all_notifications(payload)
    results["webhooks"] = webhook_results

    logger.info(
        "message_processed",
        topic=topic,
        incident_id=payload.get("incident_id", payload.get("id")),
        results=results,
    )


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
async def _start_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        *settings.KAFKA_TOPICS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        auto_commit_interval_ms=5000,
        max_poll_records=10,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        value_deserializer=lambda v: __import__("json").loads(v.decode("utf-8")) if v else {},
    )

    await consumer.start()
    logger.info(
        "kafka_consumer_started",
        topics=settings.KAFKA_TOPICS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP,
    )
    return consumer


async def _consume_messages(consumer: AIOKafkaConsumer) -> None:
    try:
        async for message in consumer:
            if _shutdown_event.is_set():
                break

            topic = message.topic
            partition = message.partition
            offset = message.offset

            logger.debug(
                "message_received",
                topic=topic,
                partition=partition,
                offset=offset,
            )

            try:
                enriched = {
                    "value": message.value,
                    "topic": topic,
                    "partition": partition,
                    "offset": offset,
                    "timestamp": message.timestamp,
                }
                await _process_message(enriched, topic)
            except Exception as exc:
                logger.error(
                    "message_processing_error",
                    topic=topic,
                    partition=partition,
                    offset=offset,
                    error=str(exc),
                    exc_info=True,
                )
    except Exception as exc:
        logger.error("consumer_loop_error", error=str(exc), exc_info=True)
        raise


async def _handle_shutdown(consumer: AIOKafkaConsumer) -> None:
    _shutdown_event.set()
    logger.info("shutdown_signal_received")

    await consumer.stop()
    await email_notifier.disconnect()
    await webhook_notifier.close()

    logger.info("notification_service_stopped")


def _signal_handler() -> None:
    _shutdown_event.set()


async def main() -> None:
    _setup_logging()
    logger.info("notification_service_starting")

    await email_notifier.connect()

    consumer = await _start_consumer()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    try:
        await _consume_messages(consumer)
    finally:
        await _handle_shutdown(consumer)


if __name__ == "__main__":
    asyncio.run(main())
