from __future__ import annotations

import sys
import time

import pytest

ROOT = str(__import__("pathlib").Path(__file__).resolve().parent.parent.parent)
DETECTION_SVC = str(__import__("pathlib").Path(ROOT) / "services" / "detection-service")
if DETECTION_SVC not in sys.path:
    sys.path.insert(0, DETECTION_SVC)

from detection.engine.rules import DetectionHit, RuleEngine


@pytest.fixture
def engine():
    return RuleEngine()


# ── Brute Force Detection ────────────────────────────────────────────────
def test_brute_force_below_threshold(engine: RuleEngine):
    event = {
        "action": "login_failed",
        "source_ip": "10.0.0.1",
        "user": "admin",
    }
    for _ in range(5):
        hits = engine.evaluate(event)
    assert len(hits) == 0


def test_brute_force_above_threshold(engine: RuleEngine):
    event = {
        "action": "login_failed",
        "source_ip": "10.0.0.1",
        "user": "admin",
    }
    hits = []
    for _ in range(12):
        hits = engine.evaluate(event)
    assert len(hits) >= 1
    assert hits[0].rule_id == "BRUTE-FORCE-001"
    assert hits[0].severity == "high"
    assert hits[0].mitre_technique == "T1110"
    assert hits[0].source_ip == "10.0.0.1"
    assert hits[0].event_count > 10


def test_brute_force_different_ips(engine: RuleEngine):
    for i in range(12):
        engine.evaluate({
            "action": "login_failed",
            "source_ip": f"10.0.0.{i % 2}",
            "user": "admin",
        })
    hits_0 = engine.evaluate({
        "action": "login_failed",
        "source_ip": "10.0.0.0",
        "user": "admin",
    })
    hits_1 = engine.evaluate({
        "action": "login_failed",
        "source_ip": "10.0.0.1",
        "user": "admin",
    })
    assert len(hits_0) >= 1
    assert len(hits_1) >= 1


def test_brute_force_with_status_field(engine: RuleEngine):
    event = {
        "status": "failure",
        "source_ip": "192.168.1.50",
        "user": "root",
    }
    hits = []
    for _ in range(15):
        hits = engine.evaluate(event)
    assert len(hits) >= 1
    assert hits[0].source_ip == "192.168.1.50"


# ── Port Scan Detection ──────────────────────────────────────────────────
def test_port_scan_below_threshold(engine: RuleEngine):
    for port in range(10):
        engine.evaluate({
            "source_ip": "10.0.0.2",
            "destination_port": port,
            "category": "network",
        })
    hits = engine.evaluate({
        "source_ip": "10.0.0.2",
        "destination_port": 99,
        "category": "network",
    })
    assert len(hits) == 0


def test_port_scan_above_threshold(engine: RuleEngine):
    for port in range(30):
        hits = engine.evaluate({
            "source_ip": "10.0.0.2",
            "destination_port": port,
            "category": "network",
        })
    assert len(hits) >= 1
    assert hits[0].rule_id == "PORT-SCAN-001"
    assert hits[0].severity == "high"
    assert hits[0].mitre_technique == "T1046"


# ── Privilege Escalation Detection ───────────────────────────────────────
def test_privilege_escalation_sudo(engine: RuleEngine):
    hits = engine.evaluate({
        "action": "sudo",
        "source_ip": "10.0.0.3",
        "user": "analyst1",
    })
    assert len(hits) == 1
    assert hits[0].rule_id == "PRIV-ESC-001"
    assert hits[0].severity == "critical"
    assert hits[0].mitre_technique == "T1548"


def test_privilege_escalation_role_added(engine: RuleEngine):
    hits = engine.evaluate({
        "action": "role_added",
        "source_ip": "10.0.0.4",
        "user": "dev01",
    })
    assert len(hits) == 1
    assert hits[0].rule_id == "PRIV-ESC-001"


def test_privilege_escalation_account_modified(engine: RuleEngine):
    hits = engine.evaluate({
        "action": "account_modified",
        "source_ip": "10.0.0.5",
        "user": "admin",
    })
    assert len(hits) == 1


def test_no_privilege_escalation_on_normal_action(engine: RuleEngine):
    hits = engine.evaluate({
        "action": "file_access",
        "source_ip": "10.0.0.6",
        "user": "user1",
    })
    assert len(hits) == 0


# ── Unusual Hours Login ──────────────────────────────────────────────────
def test_unusual_hours_login(engine: RuleEngine):
    from datetime import datetime, timezone

    night_ts = datetime(2026, 1, 15, 23, 30, 0, tzinfo=timezone.utc).isoformat()
    hits = engine.evaluate({
        "action": "login",
        "source_ip": "10.0.0.7",
        "user": "nightworker",
        "status": "success",
        "timestamp": night_ts,
    })
    assert len(hits) == 1
    assert hits[0].rule_id == "UNUSUAL-HOURS-001"
    assert hits[0].severity == "medium"


def test_normal_hours_login_no_hit(engine: RuleEngine):
    from datetime import datetime, timezone

    day_ts = datetime(2026, 1, 15, 14, 0, 0, tzinfo=timezone.utc).isoformat()
    hits = engine.evaluate({
        "action": "login",
        "source_ip": "10.0.0.8",
        "user": "dayworker",
        "status": "success",
        "timestamp": day_ts,
    })
    assert len(hits) == 0


def test_failed_login_not_flagged_unusual_hours(engine: RuleEngine):
    from datetime import datetime, timezone

    night_ts = datetime(2026, 1, 15, 2, 0, 0, tzinfo=timezone.utc).isoformat()
    hits = engine.evaluate({
        "action": "login_failed",
        "source_ip": "10.0.0.9",
        "user": "unknown",
        "status": "failure",
        "timestamp": night_ts,
    })
    assert len(hits) == 0


# ── Multiple Rules Fire on Complex Event ─────────────────────────────────
def test_multiple_rules_cannot_fire_on_single_event(engine: RuleEngine):
    hits = engine.evaluate({
        "action": "sudo",
        "source_ip": "10.0.0.10",
        "user": "admin",
        "destination_port": 8080,
    })
    rule_ids = [h.rule_id for h in hits]
    assert "PRIV-ESC-001" in rule_ids


# ── Cleanup ──────────────────────────────────────────────────────────────
def test_cleanup(engine: RuleEngine):
    for _ in range(12):
        engine.evaluate({
            "action": "login_failed",
            "source_ip": "10.0.0.99",
            "user": "admin",
        })
    engine.cleanup()
    assert len(engine._failed_logins) == 0
