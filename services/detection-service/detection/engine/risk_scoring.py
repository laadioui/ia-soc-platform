from __future__ import annotations

import structlog

logger = structlog.get_logger()

# Weights — must sum to 100
WEIGHTS = {
    "ip_reputation": 20,
    "event_severity": 25,
    "frequency": 15,
    "user_risk": 10,
    "behavior_anomaly": 20,
    "mitre_mapping": 10,
}

SEVERITY_MAP = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.3,
    "info": 0.1,
    "informational": 0.1,
}

KNOWN_BAD_IPS: set[str] = set()
HIGH_RISK_USERS: set[str] = set()


class RiskScorer:
    """Compute a composite risk score (0-100) for a detection hit or event."""

    def __init__(self) -> None:
        self._frequency_cache: dict[str, int] = {}

    def score(
        self,
        *,
        source_ip: str | None = None,
        severity: str = "medium",
        frequency: int | None = None,
        user: str | None = None,
        behavior_anomaly_score: float | None = None,
        mitre_technique: str | None = None,
    ) -> tuple[float, dict[str, float]]:
        components: dict[str, float] = {}

        # IP reputation (0-1) — unknown IPs get a neutral prior
        if source_ip is None:
            ip_score = 0.5
        elif source_ip in KNOWN_BAD_IPS:
            ip_score = 1.0
        else:
            ip_score = 0.1
        components["ip_reputation"] = ip_score

        # Event severity (0-1)
        components["event_severity"] = SEVERITY_MAP.get(severity.lower(), 0.5)

        # Frequency (0-1) — normalise against a reasonable cap; unknown -> neutral
        freq_score = 0.5 if frequency is None else min(frequency / 50.0, 1.0)
        components["frequency"] = freq_score

        # User risk (0-1) — unknown users get a neutral prior
        if user is None:
            user_score = 0.5
        elif user in HIGH_RISK_USERS:
            user_score = 1.0
        else:
            user_score = 0.2
        components["user_risk"] = user_score

        # Behavior anomaly (0-1) — unknown -> neutral
        components["behavior_anomaly"] = 0.5 if behavior_anomaly_score is None else max(0.0, min(behavior_anomaly_score, 1.0))

        # MITRE mapping (0-1) — if a technique is present, bump score
        if mitre_technique is None:
            mitre_score = 0.5
        elif mitre_technique:
            mitre_score = 0.8
        else:
            mitre_score = 0.2
        components["mitre_mapping"] = mitre_score

        weighted = sum(
            components[k] * (WEIGHTS[k] / 100.0) for k in WEIGHTS
        )
        total = round(weighted * 100, 2)

        logger.debug(
            "risk_score_computed",
            total=total,
            components=components,
            source_ip=source_ip,
        )
        return total, components

    def score_hit(self, hit_dict: dict) -> tuple[float, dict[str, float]]:
        """Convenience wrapper that extracts fields from a detection-hit dict."""
        return self.score(
            source_ip=hit_dict.get("source_ip", ""),
            severity=hit_dict.get("severity", "medium"),
            frequency=hit_dict.get("event_count", 1),
            user=hit_dict.get("user", ""),
            behavior_anomaly_score=hit_dict.get("behavior_anomaly_score", 0.0),
            mitre_technique=hit_dict.get("mitre_technique", ""),
        )

    def update_frequency(self, key: str, amount: int = 1) -> int:
        self._frequency_cache[key] = self._frequency_cache.get(key, 0) + amount
        return self._frequency_cache[key]

    def get_frequency(self, key: str) -> int:
        return self._frequency_cache.get(key, 0)

    def reset_frequency(self, key: str) -> None:
        self._frequency_cache.pop(key, None)

    def cleanup_stale(self, max_age_seconds: int = 7200) -> None:
        # Simple periodic wipe — in production use an LRU / TTL cache
        if len(self._frequency_cache) > 10_000:
            self._frequency_cache.clear()
