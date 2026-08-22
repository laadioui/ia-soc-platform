from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


async def _create_alert_in_db(session: AsyncSession) -> Alert:
    alert = Alert(
        id=uuid.uuid4(),
        alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        title="Brute Force Detected",
        description="Multiple failed login attempts from single IP",
        severity="high",
        status="new",
        risk_score=75.0,
        source="detection-engine",
        rule_id="BRUTE-FORCE-001",
        rule_name="Brute Force Login Attempt",
        event_count=15,
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


# ── List Alerts ──────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_alerts_empty(client: AsyncClient):
    resp = await client.get("/api/v1/alerts/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["alerts"] == []


@pytest.mark.asyncio
async def test_list_alerts_with_data(client: AsyncClient, db_session: AsyncSession):
    await _create_alert_in_db(db_session)
    await _create_alert_in_db(db_session)

    resp = await client.get("/api/v1/alerts/")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_list_alerts_filter_severity(client: AsyncClient, db_session: AsyncSession):
    for sev in ["critical", "high", "low"]:
        alert = Alert(
            id=uuid.uuid4(),
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            title=f"{sev} alert",
            severity=sev,
            status="new",
            source="detection-engine",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
        )
        db_session.add(alert)
    await db_session.commit()

    resp = await client.get("/api/v1/alerts/?severity=critical")
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_list_alerts_filter_status(client: AsyncClient, db_session: AsyncSession):
    for st in ["new", "acknowledged", "new"]:
        alert = Alert(
            id=uuid.uuid4(),
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            title=f"alert-{st}",
            severity="medium",
            status=st,
            source="detection-engine",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
        )
        db_session.add(alert)
    await db_session.commit()

    resp = await client.get("/api/v1/alerts/?status=new")
    assert resp.json()["total"] == 2


# ── Get Alert ────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_alert_by_id(client: AsyncClient, db_session: AsyncSession):
    alert = await _create_alert_in_db(db_session)
    resp = await client.get(f"/api/v1/alerts/{alert.id}")
    assert resp.status_code == 200
    assert resp.json()["alert_id"] == alert.alert_id


@pytest.mark.asyncio
async def test_get_alert_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/alerts/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Update Alert ─────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_alert_status(client: AsyncClient, db_session: AsyncSession):
    alert = await _create_alert_in_db(db_session)
    resp = await client.put(
        f"/api/v1/alerts/{alert.id}",
        json={"status": "acknowledged"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"


@pytest.mark.asyncio
async def test_update_alert_not_found(client: AsyncClient):
    resp = await client.put(
        f"/api/v1/alerts/{uuid.uuid4()}",
        json={"status": "resolved"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_alert_multiple_fields(client: AsyncClient, db_session: AsyncSession):
    alert = await _create_alert_in_db(db_session)
    resp = await client.put(
        f"/api/v1/alerts/{alert.id}",
        json={"status": "resolved", "severity": "low"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "resolved"
    assert body["severity"] == "low"


# ── Alert Lifecycle ──────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_alert_lifecycle(client: AsyncClient, db_session: AsyncSession):
    alert = await _create_alert_in_db(db_session)

    resp = await client.put(
        f"/api/v1/alerts/{alert.id}",
        json={"status": "acknowledged"},
    )
    assert resp.json()["status"] == "acknowledged"

    resp = await client.put(
        f"/api/v1/alerts/{alert.id}",
        json={"status": "investigating"},
    )
    assert resp.json()["status"] == "investigating"

    resp = await client.put(
        f"/api/v1/alerts/{alert.id}",
        json={"status": "resolved"},
    )
    assert resp.json()["status"] == "resolved"
