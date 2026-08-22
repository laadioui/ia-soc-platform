from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident


async def _create_incident_in_db(session: AsyncSession, **overrides) -> Incident:
    defaults = dict(
        id=uuid.uuid4(),
        incident_id=f"INC-2026-{uuid.uuid4().hex[:4].upper()}",
        title="Brute Force Campaign",
        description="Coordinated brute force from 192.168.1.100",
        severity="high",
        status="new",
        risk_score=72.5,
        source="detection-engine",
    )
    defaults.update(overrides)
    incident = Incident(**defaults)
    session.add(incident)
    await session.commit()
    await session.refresh(incident)
    return incident


# ── Create Incident ──────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient):
    resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Data Exfiltration",
            "description": "Possible data exfil via DNS tunneling",
            "severity": "critical",
            "risk_score": 90.0,
            "source": "correlation-engine",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["incident_id"].startswith("INC-")
    assert body["title"] == "Data Exfiltration"
    assert body["severity"] == "critical"
    assert body["status"] == "new"


@pytest.mark.asyncio
async def test_create_incident_minimal(client: AsyncClient):
    resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Suspicious Activity",
            "severity": "medium",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["risk_score"] == 0.0


@pytest.mark.asyncio
async def test_create_incident_missing_required(client: AsyncClient):
    resp = await client.post("/api/v1/incidents/", json={})
    assert resp.status_code == 422


# ── List Incidents ───────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_incidents_empty(client: AsyncClient):
    resp = await client.get("/api/v1/incidents/")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_list_incidents_with_data(client: AsyncClient, db_session: AsyncSession):
    await _create_incident_in_db(db_session)
    await _create_incident_in_db(db_session)

    resp = await client.get("/api/v1/incidents/")
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_list_incidents_filter_severity(client: AsyncClient, db_session: AsyncSession):
    await _create_incident_in_db(db_session, severity="critical")
    await _create_incident_in_db(db_session, severity="low")

    resp = await client.get("/api/v1/incidents/?severity=critical")
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_list_incidents_filter_status(client: AsyncClient, db_session: AsyncSession):
    await _create_incident_in_db(db_session, status="new")
    await _create_incident_in_db(db_session, status="resolved")
    await _create_incident_in_db(db_session, status="new")

    resp = await client.get("/api/v1/incidents/?status=new")
    assert resp.json()["total"] == 2


# ── Get Incident ─────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_incident_by_id(client: AsyncClient, db_session: AsyncSession):
    inc = await _create_incident_in_db(db_session)
    resp = await client.get(f"/api/v1/incidents/{inc.id}")
    assert resp.status_code == 200
    assert resp.json()["incident_id"] == inc.incident_id


@pytest.mark.asyncio
async def test_get_incident_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/incidents/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Update Incident ──────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_incident_status(client: AsyncClient, db_session: AsyncSession):
    inc = await _create_incident_in_db(db_session)
    resp = await client.put(
        f"/api/v1/incidents/{inc.id}",
        json={"status": "investigating"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "investigating"


@pytest.mark.asyncio
async def test_update_incident_severity(client: AsyncClient, db_session: AsyncSession):
    inc = await _create_incident_in_db(db_session)
    resp = await client.put(
        f"/api/v1/incidents/{inc.id}",
        json={"severity": "critical"},
    )
    assert resp.json()["severity"] == "critical"


@pytest.mark.asyncio
async def test_update_incident_not_found(client: AsyncClient):
    resp = await client.put(
        f"/api/v1/incidents/{uuid.uuid4()}",
        json={"status": "resolved"},
    )
    assert resp.status_code == 404


# ── Incident Timeline ────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_incident_timeline(client: AsyncClient, db_session: AsyncSession):
    inc = await _create_incident_in_db(db_session)
    resp = await client.get(f"/api/v1/incidents/{inc.id}/timeline")
    assert resp.status_code == 200
    body = resp.json()
    assert "events" in body
    assert "alerts" in body
    assert "iocs" in body
    assert "mitre_techniques" in body
    assert "response_actions" in body
    assert "ai_analyses" in body


@pytest.mark.asyncio
async def test_incident_timeline_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/incidents/{uuid.uuid4()}/timeline")
    assert resp.status_code == 404


# ── Full Lifecycle ───────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_incident_full_lifecycle(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "APT Campaign",
            "severity": "high",
            "risk_score": 80.0,
        },
    )
    inc_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "investigating", "severity": "critical"},
    )
    assert resp.json()["status"] == "investigating"
    assert resp.json()["severity"] == "critical"

    resp = await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "contained"},
    )
    assert resp.json()["status"] == "contained"

    resp = await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "resolved"},
    )
    assert resp.json()["status"] == "resolved"

    get_resp = await client.get(f"/api/v1/incidents/{inc_id}")
    assert get_resp.json()["status"] == "resolved"
