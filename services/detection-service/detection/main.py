from __future__ import annotations

import json
import signal
import sys
import time
from typing import Any

import orjson
import structlog
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from detection.config import settings
from detection.engine.correlation import CorrelationEngine
from detection.engine.risk_scoring import RiskScorer
from detection.engine.rules import DetectionHit, RuleEngine
from detection.engine.sigma import SigmaEvaluator

# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if sys.stderr.isatty() else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        structlog.get_config()["wrapper_class"].level
        if hasattr(structlog.get_config().get("wrapper_class", object), "level")
        else 0
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------
EVENTS_CONSUMED = Counter("detection_events_consumed_total", "Events consumed from Kafka")
ALERTS_PRODUCED = Counter("detection_alerts_produced_total", "Alerts produced to Kafka")
INCIDENTS_PRODUCED = Counter("detection_incidents_produced_total", "Incidents produced to Kafka")
EVENT_PROCESSING_TIME = Histogram("detection_event_processing_seconds", "Time to process one event")
ACTIVE_EVENTS = Gauge("detection_active_events", "Events currently being tracked in correlation")
DETECTION_ERRORS = Counter("detection_errors_total", "Processing errors", ["error_type"])

# ---------------------------------------------------------------------------
# Kafka helpers
# ---------------------------------------------------------------------------
KAFKA_COMMON: dict[str, Any] = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "security.protocol": settings.KAFKA_SECURITY_PROTOCOL,
}


def _delivery_cb(err, msg):
    if err:
        logger.error("kafka_produce_failed", error=str(err), topic=msg.topic() if msg else "?")


def build_consumer() -> Consumer:
    conf = {
        **KAFKA_COMMON,
        "group.id": settings.KAFKA_CONSUMER_GROUP,
        "auto.offset.reset": settings.KAFKA_AUTO_OFFSET_RESET,
        "enable.auto.commit": True,
        "max.poll.interval.ms": 300_000,
        "session.timeout.ms": 30_000,
    }
    return Consumer(conf)


def build_producer() -> Producer:
    conf = {
        **KAFKA_COMMON,
        "linger.ms": 50,
        "batch.num.messages": 100,
    }
    return Producer(conf)


def produce_json(producer: Producer, topic: str, payload: dict) -> None:
    try:
        data = orjson.dumps(payload)
        producer.produce(topic, value=data, callback=_delivery_cb)
        producer.poll(0)
    except KafkaException as exc:
        logger.error("kafka_produce_error", topic=topic, error=str(exc))
        DETECTION_ERRORS.labels(error_type="produce").inc()


# ---------------------------------------------------------------------------
# Event decoder
# ---------------------------------------------------------------------------
def decode_event(raw_bytes: bytes | None) -> dict | None:
    if raw_bytes is None:
        return None
    try:
        return orjson.loads(raw_bytes)
    except Exception:
        try:
            return json.loads(raw_bytes)
        except Exception:
            logger.warning("event_decode_failed")
            return None


# ---------------------------------------------------------------------------
# Main processing loop
# ---------------------------------------------------------------------------
def run() -> None:
    # Prometheus
    start_http_server(9100)
    logger.info("metrics_server_started", port=9100)

    rule_engine = RuleEngine()
    sigma = SigmaEvaluator()
    scorer = RiskScorer()
    correlator = CorrelationEngine()

    consumer = build_consumer()
    producer = build_producer()

    running = True

    def _shutdown(signum, _frame):
        nonlocal running
        logger.info("shutdown_signal", signal=signum)
        running = False

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    topics = [settings.KAFKA_TOPIC_SECURITY_EVENTS]
    consumer.subscribe(topics)
    logger.info(
        "consumer_started",
        topics=topics,
        group=settings.KAFKA_CONSUMER_GROUP,
        bootstrap=settings.KAFKA_BOOTSTRAP_SERVERS,
    )

    tick_interval = 30.0
    last_tick = time.time()

    while running:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            code = msg.error().code()
            if code == KafkaError._PARTITION_EOF:
                continue
            logger.error("kafka_consume_error", error=str(msg.error()))
            DETECTION_ERRORS.labels(error_type="consume").inc()
            continue

        EVENTS_CONSUMED.inc()

        event = decode_event(msg.value())
        if event is None:
            DETECTION_ERRORS.labels(error_type="decode").inc()
            continue

        with EVENT_PROCESSING_TIME.time():
            # --- 1. Rule engine ---
            hits = rule_engine.evaluate(event)

            # --- 2. Sigma rules ---
            sigma_hits = sigma.evaluate(event)
            for sh in sigma_hits:
                sh["source_ip"] = event.get("source_ip", event.get("src_ip", ""))
                sh["user"] = event.get("user", event.get("username", ""))
                sh["event_count"] = 1
            hits.extend(
                DetectionHit(
                    rule_id=h["rule_id"],
                    rule_name=h["rule_name"],
                    severity=h["severity"],
                    description=h["description"],
                    mitre_tactic=h.get("mitre_tactic", ""),
                    mitre_technique=h.get("mitre_technique", ""),
                    source_ip=h.get("source_ip", ""),
                    user=h.get("user", ""),
                    event_count=h.get("event_count", 1),
                    confidence=h.get("confidence", 0.5),
                    metadata={k: v for k, v in h.items() if k not in ("rule_id", "rule_name", "severity", "description")},
                )
                for h in sigma_hits
            )

            # --- 3. Risk scoring ---
            for hit in hits:
                risk_score, components = scorer.score(
                    source_ip=hit.source_ip,
                    severity=hit.severity,
                    frequency=hit.event_count,
                    user=hit.user,
                    mitre_technique=hit.mitre_technique,
                )

                alert = {
                    "alert_id": f"{hit.rule_id}-{int(time.time() * 1000)}",
                    "rule_id": hit.rule_id,
                    "rule_name": hit.rule_name,
                    "severity": hit.severity,
                    "description": hit.description,
                    "mitre_tactic": hit.mitre_tactic,
                    "mitre_technique": hit.mitre_technique,
                    "source_ip": hit.source_ip,
                    "user": hit.user,
                    "event_count": hit.event_count,
                    "confidence": hit.confidence,
                    "risk_score": risk_score,
                    "risk_components": components,
                    "source_event": event,
                    "timestamp": time.time(),
                }

                produce_json(producer, settings.KAFKA_TOPIC_ALERTS, alert)
                ALERTS_PRODUCED.inc()
                logger.info(
                    "alert_generated",
                    rule_id=hit.rule_id,
                    severity=hit.severity,
                    risk_score=risk_score,
                    source_ip=hit.source_ip,
                )

                # --- 4. Correlation ---
                incident = correlator.add_hit(alert)
                if incident is not None:
                    produce_json(producer, settings.KAFKA_TOPIC_INCIDENTS, incident)
                    INCIDENTS_PRODUCED.inc()
                    logger.info("incident_created", incident_id=incident["incident_id"])

        # Periodic correlation tick & cleanup
        now = time.time()
        if now - last_tick >= tick_interval:
            finalised = correlator.tick()
            for inc in finalised:
                produce_json(producer, settings.KAFKA_TOPIC_INCIDENTS, inc)
                INCIDENTS_PRODUCED.inc()
            rule_engine.cleanup()
            scorer.cleanup_stale()
            ACTIVE_EVENTS.set(correlator.open_incident_count)
            last_tick = now

    logger.info("consumer_stopping")
    # Flush remaining messages
    producer.flush(timeout=10)
    consumer.close()
    logger.info("consumer_stopped")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info(
        "detection_service_starting",
        version=settings.APP_VERSION,
        env=settings.ENVIRONMENT,
    )
    run()
