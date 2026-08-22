from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_event_and_verify_in_list(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/events/",
        json={
            "source": "linux-syslog",
            "source_type": "linux",
            "category": "authentication",
            "action": "login_failed",
            "severity": "high",
            "source_ip": "192.168.1.100",
            "user_name": "root",
            "hostname": "webserver-01",
            "tags": ["brute-force", "suspicious"],
        },
    )
    assert create_resp.status_code == 201
    event_id = create_resp.json()["id"]

    list_resp = await client.get("/api/v1/events/")
    assert list_resp.status_code == 200
    events = list_resp.json()["events"]
    assert any(e["id"] == event_id for e in events)


@pytest.mark.asyncio
async def test_create_event_get_by_id(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/events/",
        json={
            "source": "windows-eventlog",
            "source_type": "windows",
            "category": "process",
            "action": "process_created",
            "severity": "medium",
            "source_ip": "10.0.0.50",
            "user_name": "SYSTEM",
            "hostname": "dc-01",
        },
    )
    event_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/events/{event_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["source"] == "windows-eventlog"
    assert body["user_name"] == "SYSTEM"
    assert body["hostname"] == "dc-01"


@pytest.mark.asyncio
async def test_bulk_ingest_then_filter(client: AsyncClient):
    events = []
    for i in range(10):
        events.append({
            "source": "syslog",
            "source_type": "linux",
            "category": "authentication",
            "action": "login",
            "severity": "high" if i < 3 else "low",
            "source_ip": f"192.168.1.{i}",
        })

    bulk_resp = await client.post("/api/v1/events/bulk", json={"events": events})
    assert bulk_resp.status_code == 201
    assert bulk_resp.json()["ingested"] == 10

    high_resp = await client.get("/api/v1/events/?severity=high")
    assert high_resp.json()["total"] == 3

    low_resp = await client.get("/api/v1/events/?severity=low")
    assert low_resp.json()["total"] == 7


@pytest.mark.asyncio
async def test_event_source_ip_correlation(client: AsyncClient):
    src_ip = "10.99.99.99"
    for i in range(5):
        await client.post(
            "/api/v1/events/",
            json={
                "source": "firewall",
                "source_type": "network",
                "category": "network",
                "action": "connection_attempt",
                "severity": "info",
                "source_ip": src_ip,
                "destination_port": 1024 + i,
            },
        )

    resp = await client.get(f"/api/v1/events/?source_ip={src_ip}")
    assert resp.json()["total"] == 5

    for evt in resp.json()["events"]:
        assert evt["source_ip"] == src_ip


@pytest.mark.asyncio
async def test_create_get_update_alert_flow(client: AsyncClient):
    create_evt = await client.post(
        "/api/v1/events/",
        json={
            "source": "ids",
            "source_type": "network",
            "category": "intrusion",
            "action": "signature_match",
            "severity": "critical",
            "source_ip": "10.0.0.200",
        },
    )

    inc_resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "IDS Signature Match",
            "severity": "critical",
            "risk_score": 95.0,
            "source": "ids-suricata",
        },
    )
    assert inc_resp.status_code == 201
    inc_id = inc_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "investigating"},
    )
    assert update_resp.json()["status"] == "investigating"

    timeline_resp = await client.get(f"/api/v1/incidents/{inc_id}/timeline")
    assert timeline_resp.status_code == 200


@pytest.mark.asyncio
async def test_event_list_pagination_across_pages(client: AsyncClient):
    for i in range(12):
        await client.post(
            "/api/v1/events/",
            json={
                "source": "syslog",
                "source_type": "linux",
                "category": "system",
                "action": "service_start",
                "severity": "info",
            },
        )

    page1 = await client.get("/api/v1/events/?page=1&page_size=5")
    page2 = await client.get("/api/v1/events/?page=2&page_size=5")
    page3 = await client.get("/api/v1/events/?page=3&page_size=5")

    assert page1.json()["total"] == 12
    assert len(page1.json()["events"]) == 5
    assert len(page2.json()["events"]) == 5
    assert len(page3.json()["events"]) == 2

    ids_p1 = {e["id"] for e in page1.json()["events"]}
    ids_p2 = {e["id"] for e in page2.json()["events"]}
    assert ids_p1.isdisjoint(ids_p2)
