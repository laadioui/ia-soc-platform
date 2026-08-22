from __future__ import annotations

import sys
import time

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

ROOT = str(__import__("pathlib").Path(__file__).resolve().parent.parent.parent)
DETECTION_SVC = str(__import__("pathlib").Path(ROOT) / "services" / "detection-service")
if DETECTION_SVC not in sys.path:
    sys.path.insert(0, DETECTION_SVC)

from detection.engine.rules import RuleEngine
from detection.engine.risk_scoring import RiskScorer
from detection.engine.correlation import CorrelationEngine


@pytest.fixture
def pipeline():
    rule_engine = RuleEngine()
    scorer = RiskScorer()
    correlator = CorrelationEngine()
    return rule_engine, scorer, correlator


def _run_event(pipeline, event):
    rule_engine, scorer, correlator = pipeline
    hits = rule_engine.evaluate(event)
    alerts = []
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
        alerts.append(alert)
        incident = correlator.add_hit(alert)
    return hits, alerts


# ── Brute Force → Alert Pipeline ────────────────────────────────────────
def test_brute_force_generates_alert(pipeline):
    event_template = {
        "action": "login_failed",
        "source_ip": "192.168.1.100",
        "user": "root",
    }
    all_alerts = []
    for _ in range(12):
        hits, alerts = _run_event(pipeline, event_template)
        all_alerts.extend(alerts)

    assert len(all_alerts) >= 1
    alert = all_alerts[-1]
    assert alert["rule_id"] == "BRUTE-FORCE-001"
    assert alert["severity"] == "high"
    assert alert["risk_score"] > 0
    assert alert["source_ip"] == "192.168.1.100"


# ── Port Scan → Alert Pipeline ──────────────────────────────────────────
def test_port_scan_generates_alert(pipeline):
    all_alerts = []
    for port in range(30):
        hits, alerts = _run_event(pipeline, {
            "source_ip": "10.0.0.50",
            "destination_port": port,
        })
        all_alerts.extend(alerts)

    assert len(all_alerts) >= 1
    port_scan_alert = [a for a in all_alerts if a["rule_id"] == "PORT-SCAN-001"]
    assert len(port_scan_alert) >= 1
    assert port_scan_alert[0]["source_ip"] == "10.0.0.50"


# ── Privilege Escalation → Alert → Incident Pipeline ────────────────────
def test_priv_esc_generates_alert_and_incident(pipeline):
    _, _, correlator = pipeline
    hits, alerts = _run_event(pipeline, {
        "action": "sudo",
        "source_ip": "10.0.0.25",
        "user": "analyst1",
    })
    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "PRIV-ESC-001"
    assert alerts[0]["severity"] == "critical"

    incident = correlator.add_hit(alerts[0])
    assert incident is not None
    assert incident["status"] == "open"
    assert "10.0.0.25" in incident["source_ips"]


# ── Full Kill Chain Simulation ──────────────────────────────────────────
def test_full_kill_chain(pipeline):
    rule_engine, scorer, correlator = pipeline
    attacker_ip = "192.168.1.100"

    for _ in range(15):
        _run_event(pipeline, {
            "action": "login_failed",
            "source_ip": attacker_ip,
            "user": "admin",
        })

    hits, alerts = _run_event(pipeline, {
        "action": "login",
        "source_ip": attacker_ip,
        "user": "admin",
        "status": "success",
        "timestamp": "2026-01-15T23:30:00+00:00",
    })

    hits, alerts = _run_event(pipeline, {
        "action": "sudo",
        "source_ip": attacker_ip,
        "user": "admin",
    })

    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"
    assert alerts[0]["mitre_technique"] == "T1548"

    hits, alerts = _run_event(pipeline, {
        "source_ip": attacker_ip,
        "destination_port": 445,
        "action": "smb_connection",
    })

    hits, alerts = _run_event(pipeline, {
        "action": "login",
        "source_ip": "10.0.0.25",
        "user": "admin",
        "status": "success",
        "hostname": "fileserver-01",
        "timestamp": "2026-01-15T23:45:00+00:00",
    })

    open_count = correlator.open_incident_count
    assert open_count >= 1


# ── Event → Detection → Alert stored in DB ──────────────────────────────
@pytest.mark.asyncio
async def test_event_to_alert_in_database(client: AsyncClient):
    for _ in range(12):
        resp = await client.post(
            "/api/v1/events/",
            json={
                "source": "linux-syslog",
                "source_type": "linux",
                "category": "authentication",
                "action": "login_failed",
                "severity": "high",
                "source_ip": "192.168.1.200",
                "user_name": "root",
            },
        )
        assert resp.status_code == 201

    events_resp = await client.get("/api/v1/events/?source_ip=192.168.1.200")
    assert events_resp.json()["total"] == 12


# ── No False Positives on Benign Events ─────────────────────────────────
def test_benign_events_no_alerts(pipeline):
    all_alerts = []
    for i in range(10):
        hits, alerts = _run_event(pipeline, {
            "action": "login",
            "source_ip": f"10.0.0.{i}",
            "user": f"user{i}",
            "status": "success",
            "timestamp": "2026-01-15T14:00:00+00:00",
        })
        all_alerts.extend(alerts)
    assert len(all_alerts) == 0
