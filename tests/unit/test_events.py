from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import SecurityEvent


# ── Create Event ──────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_event(client: AsyncClient):
    resp = await client.post(
        "/api/v1/events/",
        json={
            "source": "linux-syslog",
            "source_type": "linux",
            "category": "authentication",
            "action": "login_failed",
            "severity": "medium",
            "source_ip": "10.0.0.1",
            "user_name": "root",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["event_id"].startswith("evt-")
    assert body["source"] == "linux-syslog"
    assert body["severity"] == "medium"


@pytest.mark.asyncio
async def test_create_event_minimal_fields(client: AsyncClient):
    resp = await client.post(
        "/api/v1/events/",
        json={
            "source": "nginx",
            "source_type": "nginx",
            "category": "web",
            "action": "request",
            "severity": "info",
        },
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_create_event_missing_required(client: AsyncClient):
    resp = await client.post("/api/v1/events/", json={"source": "x"})
    assert resp.status_code == 422


# ── Bulk Ingest ──────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_bulk_ingest_events(client: AsyncClient):
    events = [
        {
            "source": "syslog",
            "source_type": "linux",
            "category": "auth",
            "action": "login",
            "severity": "low",
            "source_ip": f"10.0.0.{i}",
        }
        for i in range(5)
    ]
    resp = await client.post("/api/v1/events/bulk", json={"events": events})
    assert resp.status_code == 201
    assert resp.json()["ingested"] == 5


@pytest.mark.asyncio
async def test_bulk_ingest_empty(client: AsyncClient):
    resp = await client.post("/api/v1/events/bulk", json={"events": []})
    assert resp.status_code == 201
    assert resp.json()["ingested"] == 0


# ── List Events ──────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_events_empty(client: AsyncClient):
    resp = await client.get("/api/v1/events/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["events"] == []


@pytest.mark.asyncio
async def test_list_events_with_data(client: AsyncClient):
    for i in range(3):
        await client.post(
            "/api/v1/events/",
            json={
                "source": "linux-syslog",
                "source_type": "linux",
                "category": "authentication",
                "action": "login",
                "severity": "low",
            },
        )

    resp = await client.get("/api/v1/events/")
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_list_events_filter_severity(client: AsyncClient):
    for sev in ["low", "high", "low", "critical"]:
        await client.post(
            "/api/v1/events/",
            json={
                "source": "syslog",
                "source_type": "linux",
                "category": "auth",
                "action": "login",
                "severity": sev,
            },
        )

    resp = await client.get("/api/v1/events/?severity=high")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1


@pytest.mark.asyncio
async def test_list_events_filter_source(client: AsyncClient):
    for src in ["nginx", "apache", "nginx"]:
        await client.post(
            "/api/v1/events/",
            json={
                "source": src,
                "source_type": "application",
                "category": "web",
                "action": "request",
                "severity": "info",
            },
        )

    resp = await client.get("/api/v1/events/?source=nginx")
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_list_events_filter_source_ip(client: AsyncClient):
    for _ in range(3):
        await client.post(
            "/api/v1/events/",
            json={
                "source": "syslog",
                "source_type": "linux",
                "category": "auth",
                "action": "login",
                "severity": "info",
                "source_ip": "192.168.1.100",
            },
        )
    await client.post(
        "/api/v1/events/",
        json={
            "source": "syslog",
            "source_type": "linux",
            "category": "auth",
            "action": "login",
            "severity": "info",
            "source_ip": "10.0.0.1",
        },
    )

    resp = await client.get("/api/v1/events/?source_ip=192.168.1.100")
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_list_events_pagination(client: AsyncClient):
    for i in range(15):
        await client.post(
            "/api/v1/events/",
            json={
                "source": "syslog",
                "source_type": "linux",
                "category": "auth",
                "action": "login",
                "severity": "info",
            },
        )

    resp = await client.get("/api/v1/events/?page=1&page_size=5")
    body = resp.json()
    assert len(body["events"]) == 5
    assert body["total"] == 15
    assert body["page"] == 1


# ── Get Event by ID ──────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_event_by_id(client: AsyncClient):
    create = await client.post(
        "/api/v1/events/",
        json={
            "source": "syslog",
            "source_type": "linux",
            "category": "auth",
            "action": "login",
            "severity": "info",
        },
    )
    event_id = create.json()["id"]

    resp = await client.get(f"/api/v1/events/{event_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == event_id


@pytest.mark.asyncio
async def test_get_event_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/events/{fake_id}")
    assert resp.status_code == 404
