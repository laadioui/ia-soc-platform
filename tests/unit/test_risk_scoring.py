from __future__ import annotations

import sys
import math

import pytest

ROOT = str(__import__("pathlib").Path(__file__).resolve().parent.parent.parent)
DETECTION_SVC = str(__import__("pathlib").Path(ROOT) / "services" / "detection-service")
if DETECTION_SVC not in sys.path:
    sys.path.insert(0, DETECTION_SVC)

from detection.engine.risk_scoring import (
    KNOWN_BAD_IPS,
    HIGH_RISK_USERS,
    SEVERITY_MAP,
    WEIGHTS,
    RiskScorer,
)


@pytest.fixture
def scorer():
    return RiskScorer()


# ── Basic Score ──────────────────────────────────────────────────────────
def test_score_default(scorer: RiskScorer):
    score, components = scorer.score()
    assert 0 <= score <= 100
    assert isinstance(components, dict)
    assert len(components) == len(WEIGHTS)


def test_score_components_sum_to_one(scorer: RiskScorer):
    _, components = scorer.score()
    total = sum(components.values())
    assert math.isclose(total, 3.0, abs_tol=0.1)


def test_score_returns_tuple(scorer: RiskScorer):
    result = scorer.score(source_ip="1.2.3.4", severity="low", frequency=1)
    assert isinstance(result, tuple)
    assert len(result) == 2


# ── Severity Impact ──────────────────────────────────────────────────────
def test_critical_severity_higher_than_low(scorer: RiskScorer):
    crit_score, _ = scorer.score(severity="critical")
    low_score, _ = scorer.score(severity="low")
    assert crit_score > low_score


def test_all_severity_levels_in_range(scorer: RiskScorer):
    for sev in SEVERITY_MAP:
        score, _ = scorer.score(severity=sev)
        assert 0 <= score <= 100


def test_unknown_severity_defaults_to_medium(scorer: RiskScorer):
    score_unknown, _ = scorer.score(severity="weird")
    score_medium, _ = scorer.score(severity="medium")
    assert math.isclose(score_unknown, score_medium, abs_tol=1.0)


# ── Frequency Impact ─────────────────────────────────────────────────────
def test_high_frequency_higher_score(scorer: RiskScorer):
    low_freq_score, _ = scorer.score(frequency=1)
    high_freq_score, _ = scorer.score(frequency=50)
    assert high_freq_score > low_freq_score


def test_frequency_capped_at_50(scorer: RiskScorer):
    score_50, _ = scorer.score(frequency=50)
    score_100, _ = scorer.score(frequency=100)
    assert math.isclose(score_50, score_100, abs_tol=1.0)


# ── Known Bad IP ─────────────────────────────────────────────────────────
def test_known_bad_ip_increases_score(scorer: RiskScorer):
    normal_score, _ = scorer.score(source_ip="1.2.3.4")
    KNOWN_BAD_IPS.add("10.0.0.1")
    bad_score, _ = scorer.score(source_ip="10.0.0.1")
    KNOWN_BAD_IPS.discard("10.0.0.1")
    assert bad_score > normal_score


# ── High Risk User ───────────────────────────────────────────────────────
def test_high_risk_user_increases_score(scorer: RiskScorer):
    normal_score, _ = scorer.score(user="john")
    HIGH_RISK_USERS.add("admin01")
    hr_score, _ = scorer.score(user="admin01")
    HIGH_RISK_USERS.discard("admin01")
    assert hr_score > normal_score


# ── MITRE Technique ──────────────────────────────────────────────────────
def test_mitre_technique_present_increases_score(scorer: RiskScorer):
    no_mitre, _ = scorer.score(mitre_technique="")
    with_mitre, _ = scorer.score(mitre_technique="T1110")
    assert with_mitre > no_mitre


# ── Behavior Anomaly ─────────────────────────────────────────────────────
def test_behavior_anomaly_clamped(scorer: RiskScorer):
    _, components = scorer.score(behavior_anomaly_score=2.0)
    assert components["behavior_anomaly"] == 1.0

    _, components = scorer.score(behavior_anomaly_score=-5.0)
    assert components["behavior_anomaly"] == 0.0


# ── Score Hit Wrapper ────────────────────────────────────────────────────
def test_score_hit(scorer: RiskScorer):
    hit = {
        "source_ip": "192.168.1.1",
        "severity": "high",
        "event_count": 10,
        "user": "testuser",
        "mitre_technique": "T1059",
    }
    score, components = scorer.score_hit(hit)
    assert 0 <= score <= 100
    assert "event_severity" in components


# ── Frequency Cache ──────────────────────────────────────────────────────
def test_frequency_cache(scorer: RiskScorer):
    count = scorer.update_frequency("key1", 3)
    assert count == 3
    count = scorer.update_frequency("key1", 2)
    assert count == 5
    assert scorer.get_frequency("key1") == 5
    scorer.reset_frequency("key1")
    assert scorer.get_frequency("key1") == 0


# ── Extreme Combined Score ───────────────────────────────────────────────
def test_worst_case_score(scorer: RiskScorer):
    KNOWN_BAD_IPS.add("6.6.6.6")
    HIGH_RISK_USERS.add("root")
    score, _ = scorer.score(
        source_ip="6.6.6.6",
        severity="critical",
        frequency=100,
        user="root",
        behavior_anomaly_score=1.0,
        mitre_technique="T1110",
    )
    KNOWN_BAD_IPS.discard("6.6.6.6")
    HIGH_RISK_USERS.discard("root")
    assert score >= 80


def test_best_case_score(scorer: RiskScorer):
    score, _ = scorer.score(
        source_ip="1.2.3.4",
        severity="info",
        frequency=1,
        user="normaluser",
        behavior_anomaly_score=0.0,
        mitre_technique="",
    )
    assert score <= 25
