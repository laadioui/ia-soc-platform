from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC

import structlog

from detection.config import settings

logger = structlog.get_logger()


@dataclass
class DetectionHit:
    rule_id: str
    rule_name: str
    severity: str
    description: str
    mitre_tactic: str
    mitre_technique: str
    source_ip: str
    user: str
    event_count: int
    confidence: float
    metadata: dict = field(default_factory=dict)


class RuleEngine:
    """Threshold-based detection rules applied to every incoming event."""

    def __init__(self) -> None:
        self._failed_logins: dict[str, list[float]] = defaultdict(list)
        self._port_access: dict[str, list[float]] = defaultdict(list)
        self._privilege_events: dict[str, list[float]] = defaultdict(list)
        logger.info(
            "rule_engine_init",
            brute_force_threshold=settings.BRUTE_FORCE_THRESHOLD,
            brute_force_window=settings.BRUTE_FORCE_WINDOW_SECONDS,
            port_scan_threshold=settings.PORT_SCAN_THRESHOLD,
            port_scan_window=settings.PORT_SCAN_WINDOW_SECONDS,
        )

    def evaluate(self, event: dict) -> list[DetectionHit]:
        hits: list[DetectionHit] = []
        hits.extend(self._check_brute_force(event))
        hits.extend(self._check_port_scan(event))
        hits.extend(self._check_privilege_escalation(event))
        hits.extend(self._check_unusual_hours(event))
        return hits

    # ------------------------------------------------------------------
    # Brute force: >N failed logins from same IP in T seconds
    # ------------------------------------------------------------------
    def _check_brute_force(self, event: dict) -> list[DetectionHit]:
        if event.get("action") != "login_failed" and event.get("status") != "failure":
            return []

        src_ip = event.get("source_ip", event.get("src_ip", ""))
        if not src_ip:
            return []

        now = time.time()
        window = settings.BRUTE_FORCE_WINDOW_SECONDS
        cutoff = now - window
        self._failed_logins[src_ip].append(now)
        self._failed_logins[src_ip] = [t for t in self._failed_logins[src_ip] if t > cutoff]
        count = len(self._failed_logins[src_ip])

        if count > settings.BRUTE_FORCE_THRESHOLD:
            logger.warning(
                "brute_force_detected",
                source_ip=src_ip,
                count=count,
                window=window,
            )
            return [
                DetectionHit(
                    rule_id="BRUTE-FORCE-001",
                    rule_name="Brute Force Login Attempt",
                    severity="high",
                    description=(f"{count} failed login attempts from {src_ip} in the last {window}s"),
                    mitre_tactic="Credential Access",
                    mitre_technique="T1110",
                    source_ip=src_ip,
                    user=event.get("user", event.get("username", "")),
                    event_count=count,
                    confidence=min(0.5 + count * 0.05, 1.0),
                    metadata={"window_seconds": window},
                )
            ]
        return []

    # ------------------------------------------------------------------
    # Port scan: many distinct ports accessed from same IP in T seconds
    # ------------------------------------------------------------------
    def _check_port_scan(self, event: dict) -> list[DetectionHit]:
        src_ip = event.get("source_ip", event.get("src_ip", ""))
        dest_port = event.get("destination_port", event.get("dest_port"))
        if not src_ip or dest_port is None:
            return []

        now = time.time()
        window = settings.PORT_SCAN_WINDOW_SECONDS
        cutoff = now - window
        key = f"{src_ip}:{dest_port}"
        self._port_access[key].append(now)
        self._port_access[key] = [t for t in self._port_access[key] if t > cutoff]

        distinct_ports = set()
        for k in list(self._port_access.keys()):
            if k.startswith(f"{src_ip}:"):
                if any(t > cutoff for t in self._port_access[k]):
                    distinct_ports.add(int(k.split(":")[1]))
                else:
                    del self._port_access[k]

        if len(distinct_ports) > settings.PORT_SCAN_THRESHOLD:
            logger.warning(
                "port_scan_detected",
                source_ip=src_ip,
                distinct_ports=len(distinct_ports),
            )
            return [
                DetectionHit(
                    rule_id="PORT-SCAN-001",
                    rule_name="Port Scanning Activity",
                    severity="high",
                    description=(f"{src_ip} accessed {len(distinct_ports)} distinct ports in {window}s"),
                    mitre_tactic="Discovery",
                    mitre_technique="T1046",
                    source_ip=src_ip,
                    user=event.get("user", event.get("username", "")),
                    event_count=len(distinct_ports),
                    confidence=min(0.6 + len(distinct_ports) * 0.02, 1.0),
                    metadata={"distinct_ports": sorted(distinct_ports)},
                )
            ]
        return []

    # ------------------------------------------------------------------
    # Privilege escalation: sudo / role-add / group-mod events
    # ------------------------------------------------------------------
    PRIV_ESCALATION_ACTIONS = frozenset(
        {
            "sudo",
            "sudo_command",
            "role_added",
            "role_assigned",
            "group_modified",
            "permission_changed",
            "account_modified",
            "privilege_escalation",
            "added_to_admin_group",
        }
    )

    def _check_privilege_escalation(self, event: dict) -> list[DetectionHit]:
        action = event.get("action", event.get("event_type", "")).lower()
        if action not in self.PRIV_ESCALATION_ACTIONS:
            return []

        src_ip = event.get("source_ip", event.get("src_ip", ""))
        user = event.get("user", event.get("username", ""))

        logger.warning(
            "privilege_escalation_detected",
            action=action,
            source_ip=src_ip,
            user=user,
        )
        return [
            DetectionHit(
                rule_id="PRIV-ESC-001",
                rule_name="Privilege Escalation Attempt",
                severity="critical",
                description=(f"Privilege escalation event '{action}' by user '{user}' from {src_ip}"),
                mitre_tactic="Privilege Escalation",
                mitre_technique="T1548",
                source_ip=src_ip,
                user=user,
                event_count=1,
                confidence=0.85,
                metadata={"action": action},
            )
        ]

    # ------------------------------------------------------------------
    # Unusual login hours
    # ------------------------------------------------------------------
    def _check_unusual_hours(self, event: dict) -> list[DetectionHit]:
        action = event.get("action", event.get("event_type", "")).lower()
        if "login" not in action and "logon" not in action:
            return []
        # Failed logins are handled by the brute-force rule
        if event.get("status") == "failure" or "fail" in action:
            return []

        from datetime import datetime

        ts_raw = event.get("timestamp", event.get("@timestamp", ""))
        if ts_raw:
            try:
                if isinstance(ts_raw, str):
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                else:
                    ts = datetime.fromtimestamp(float(ts_raw), tz=UTC)
            except (ValueError, OSError):
                ts = datetime.now(UTC)
        else:
            ts = datetime.now(UTC)

        hour = ts.hour
        start = settings.UNUSUAL_LOGIN_START_HOUR
        end = settings.UNUSUAL_LOGIN_END_HOUR

        is_unusual = hour >= start or hour < end
        if not is_unusual:
            return []

        src_ip = event.get("source_ip", event.get("src_ip", ""))
        user = event.get("user", event.get("username", ""))

        logger.warning(
            "unusual_hours_login",
            hour=hour,
            source_ip=src_ip,
            user=user,
        )
        return [
            DetectionHit(
                rule_id="UNUSUAL-HOURS-001",
                rule_name="Unusual Login Hours",
                severity="medium",
                description=(f"Login by user '{user}' at unusual hour {hour:02d}:00 UTC from {src_ip}"),
                mitre_tactic="Defense Evasion",
                mitre_technique="T1078",
                source_ip=src_ip,
                user=user,
                event_count=1,
                confidence=0.6,
                metadata={"hour": hour},
            )
        ]

    # ------------------------------------------------------------------
    # Cleanup old tracking data
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        for store in (self._failed_logins, self._port_access, self._privilege_events):
            store.clear()
