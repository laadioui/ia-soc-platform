from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

import structlog

from detection.config import settings

logger = structlog.get_logger()


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str
    status: str
    first_seen: float
    last_seen: float
    source_ips: set[str] = field(default_factory=set)
    users: set[str] = field(default_factory=set)
    rule_ids: set[str] = field(default_factory=set)
    events: list[dict] = field(default_factory=list)
    risk_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "severity": self.severity,
            "status": self.status,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "source_ips": sorted(self.source_ips),
            "users": sorted(self.users),
            "rule_ids": sorted(self.rule_ids),
            "event_count": len(self.events),
            "risk_score": self.risk_score,
        }


class CorrelationEngine:
    """Groups related detection hits into incidents by source_ip + rule_id window."""

    def __init__(self) -> None:
        self._incidents: dict[str, Incident] = {}
        self._key_map: dict[str, str] = {}
        logger.info("correlation_engine_init")

    def _make_key(self, source_ip: str, rule_id: str) -> str:
        return f"{source_ip}|{rule_id}"

    def add_hit(self, hit_dict: dict) -> dict | None:
        """Ingest a detection hit and return an incident dict if one is finalised."""
        source_ip = hit_dict.get("source_ip", "")
        rule_id = hit_dict.get("rule_id", "")
        now = time.time()

        key = self._make_key(source_ip, rule_id)
        incident_id = self._key_map.get(key)

        if incident_id and incident_id in self._incidents:
            inc = self._incidents[incident_id]
            inc.last_seen = now
            inc.events.append(hit_dict)
            if len(inc.events) > settings.INCIDENT_MAX_EVENTS:
                return self._finalise(incident_id)
            return inc.to_dict()

        incident_id = str(uuid.uuid4())
        inc = Incident(
            incident_id=incident_id,
            title=f"{rule_id} from {source_ip}",
            severity=hit_dict.get("severity", "medium"),
            status="open",
            first_seen=now,
            last_seen=now,
            source_ips={source_ip} if source_ip else set(),
            users={hit_dict.get("user", "")} if hit_dict.get("user") else set(),
            rule_ids={rule_id} if rule_id else set(),
            events=[hit_dict],
            risk_score=hit_dict.get("risk_score", 0.0),
        )
        self._incidents[incident_id] = inc
        self._key_map[key] = incident_id
        return inc.to_dict()

    def tick(self) -> list[dict]:
        """Called periodically — finalises stale incidents and returns them."""
        now = time.time()
        finalised: list[dict] = []
        for inc_id in list(self._incidents.keys()):
            inc = self._incidents[inc_id]
            if now - inc.last_seen > settings.INCIDENT_EXPIRY_SECONDS:
                finalised.append(self._finalise(inc_id))
        return finalised

    def force_close(self, incident_id: str) -> dict | None:
        if incident_id in self._incidents:
            return self._finalise(incident_id)
        return None

    def _finalise(self, incident_id: str) -> dict:
        inc = self._incidents.pop(incident_id)
        inc.status = "resolved"

        for ip in inc.source_ips:
            for rid in inc.rule_ids:
                key = self._make_key(ip, rid)
                self._key_map.pop(key, None)

        # Aggregate risk score
        scores = [e.get("risk_score", 0) for e in inc.events if e.get("risk_score")]
        if scores:
            inc.risk_score = round(sum(scores) / len(scores), 2)

        logger.info(
            "incident_finalised",
            incident_id=incident_id,
            event_count=len(inc.events),
            severity=inc.severity,
        )
        return inc.to_dict()

    @property
    def open_incident_count(self) -> int:
        return len(self._incidents)
