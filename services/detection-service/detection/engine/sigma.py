from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import structlog
import yaml

from detection.config import settings

logger = structlog.get_logger()


class SigmaRule:
    """Minimal in-memory representation of a parsed Sigma rule."""

    def __init__(
        self,
        rule_id: str,
        title: str,
        status: str,
        description: str,
        severity: str,
        tags: list[str],
        logsource: dict[str, str],
        detection: dict[str, Any],
        falsepositives: list[str],
        raw: dict | None = None,
    ) -> None:
        self.rule_id = rule_id
        self.title = title
        self.status = status
        self.description = description
        self.severity = severity
        self.tags = tags
        self.logsource = logsource
        self.detection = detection
        self.falsepositives = falsepositives
        self.raw = raw or {}

    def __repr__(self) -> str:
        return f"SigmaRule(id={self.rule_id!r}, title={self.title!r})"


class SigmaEvaluator:
    """Loads Sigma YAML rules and evaluates them against incoming events."""

    def __init__(self, rules_path: str | Path | None = None) -> None:
        self._rules: list[SigmaRule] = []
        self._rules_path = Path(rules_path or settings.SIGMA_RULES_PATH)
        self._load_rules()

    # ------------------------------------------------------------------
    # Rule loading
    # ------------------------------------------------------------------
    def _load_rules(self) -> None:
        if not self._rules_path.exists():
            logger.warning("sigma_rules_path_missing", path=str(self._rules_path))
            return

        count = 0
        for path in sorted(self._rules_path.rglob("*.yaml")) | sorted(
            self._rules_path.rglob("*.yml")
        ):
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                if not isinstance(raw, dict):
                    continue
                self._rules.append(self._parse_rule(raw))
                count += 1
            except Exception:
                logger.exception("sigma_rule_load_error", path=str(path))

        logger.info("sigma_rules_loaded", count=count, path=str(self._rules_path))

    @staticmethod
    def _parse_rule(raw: dict[str, Any]) -> SigmaRule:
        detection = raw.get("detection", {})
        return SigmaRule(
            rule_id=raw.get("id", raw.get("title", "unknown")),
            title=raw.get("title", "Untitled"),
            status=raw.get("status", "experimental"),
            description=raw.get("description", ""),
            severity=raw.get("severity", "medium"),
            tags=raw.get("tags", []),
            logsource=raw.get("logsource", {}),
            detection=detection,
            falsepositives=raw.get("falsepositives", []),
            raw=raw,
        )

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate(self, event: dict) -> list[dict]:
        """Return list of alert dicts for rules that match *event*."""
        hits: list[dict] = []
        for rule in self._rules:
            if self._matches(rule, event):
                hits.append(
                    {
                        "rule_id": f"SIGMA-{rule.rule_id}",
                        "rule_name": rule.title,
                        "severity": rule.severity,
                        "description": rule.description,
                        "tags": rule.tags,
                        "mitre_tactic": self._extract_mitre_tactic(rule),
                        "mitre_technique": self._extract_mitre_technique(rule),
                        "sigma_status": rule.status,
                        "confidence": self._severity_to_confidence(rule.severity),
                    }
                )
        return hits

    # ------------------------------------------------------------------
    # Matching helpers
    # ------------------------------------------------------------------
    def _matches(self, rule: SigmaRule, event: dict) -> bool:
        if not self._logsource_match(rule.logsource, event):
            return False
        return self._detection_match(rule.detection, event)

    @staticmethod
    def _logsource_match(logsource: dict[str, str], event: dict) -> bool:
        if not logsource:
            return True

        category = logsource.get("category", "").lower()
        product = logsource.get("product", "").lower()
        service = logsource.get("service", "").lower()

        event_category = str(event.get("category", event.get("event_category", ""))).lower()
        event_product = str(event.get("product", event.get("event_product", ""))).lower()
        event_service = str(event.get("service", event.get("event_service", ""))).lower()

        if category and category != event_category:
            return False
        if product and product != event_product:
            return False
        if service and service != event_service:
            return False
        return True

    def _detection_match(self, detection: dict[str, Any], event: dict) -> bool:
        if not detection:
            return False

        condition = detection.get("condition", "selection")
        selectors = {k: v for k, v in detection.items() if k != "condition"}

        if not selectors:
            return False

        matched_selectors: set[str] = set()
        for sel_name, sel_body in selectors.items():
            if not isinstance(sel_body, dict):
                continue
            if self._selector_matches(sel_body, event):
                matched_selectors.add(sel_name)

        return self._eval_condition(condition, matched_selectors)

    def _selector_matches(self, selector: dict[str, Any], event: dict) -> bool:
        for field_path, expected in selector.items():
            actual = self._resolve_field(field_path, event)
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif isinstance(expected, str):
                if not self._pattern_match(expected, actual):
                    return False
            elif actual != expected:
                return False
        return True

    @staticmethod
    def _resolve_field(field_path: str, event: dict) -> Any:
        parts = field_path.split(".")
        current: Any = event
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    @staticmethod
    def _pattern_match(pattern: str, value: Any) -> bool:
        if value is None:
            return False
        str_val = str(value)
        if pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1].lower() in str_val.lower()
        if pattern.startswith("*"):
            return str_val.lower().endswith(pattern[1:].lower())
        if pattern.endswith("*"):
            return str_val.lower().startswith(pattern[:-1].lower())
        return str_val.lower() == pattern.lower()

    @staticmethod
    def _eval_condition(condition: str, matched: set[str]) -> bool:
        condition = condition.strip()

        if " or " in condition:
            parts = [p.strip() for p in condition.split(" or ")]
            return any(m in matched for m in parts)

        if " and " in condition:
            parts = [p.strip() for p in condition.split(" and ")]
            return all(m in matched for m in parts)

        if condition.startswith("not "):
            target = condition[4:].strip()
            return target not in matched

        return condition in matched

    # ------------------------------------------------------------------
    # Tag / metadata helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_mitre_tactic(rule: SigmaRule) -> str:
        for tag in rule.tags:
            if tag.lower().startswith("attack.t"):
                continue
            if "." in tag:
                parts = tag.split(".")
                if len(parts) >= 2:
                    return parts[1].replace("_", " ").title()
        return rule.raw.get("tags", [""])[0].split(".")[-1].replace("_", " ").title() if rule.tags else ""

    @staticmethod
    def _extract_mitre_technique(rule: SigmaRule) -> str:
        for tag in rule.tags:
            if tag.lower().startswith("attack.t"):
                parts = tag.split(".")
                if len(parts) >= 2:
                    return parts[-1]
        return ""

    @staticmethod
    def _severity_to_confidence(severity: str) -> float:
        return {
            "critical": 0.95,
            "high": 0.80,
            "medium": 0.60,
            "low": 0.40,
            "informational": 0.20,
        }.get(severity.lower(), 0.50)

    # ------------------------------------------------------------------
    # Hot-reload
    # ------------------------------------------------------------------
    def reload(self) -> None:
        self._rules.clear()
        self._load_rules()
