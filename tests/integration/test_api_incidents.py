from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_incident_create_list_get(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Malware Detected",
            "description": "Ransomware detected on endpoint",
            "severity": "critical",
            "risk_score": 98.0,
            "source": "edr",
        },
    )
    assert create_resp.status_code == 201
    inc_id = create_resp.json()["id"]

    list_resp = await client.get("/api/v1/incidents/")
    assert list_resp.json()["total"] >= 1

    get_resp = await client.get(f"/api/v1/incidents/{inc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Malware Detected"


@pytest.mark.asyncio
async def test_incident_full_lifecycle(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Data Breach Investigation",
            "severity": "high",
            "risk_score": 85.0,
            "source": "siem",
            "tags": ["data-breach", "pii"],
        },
    )
    inc_id = create_resp.json()["id"]

    await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "investigating", "severity": "critical"},
    )

    await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "contained"},
    )

    resp = await client.put(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "resolved"},
    )
    assert resp.json()["status"] == "resolved"

    get_resp = await client.get(f"/api/v1/incidents/{inc_id}")
    assert get_resp.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_incident_severity_escalation(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/incidents/",
        json={"title": "Suspicious Traffic", "severity": "low"},
    )
    inc_id = create_resp.json()["id"]

    for sev in ["medium", "high", "critical"]:
        resp = await client.put(
            f"/api/v1/incidents/{inc_id}",
            json={"severity": sev},
        )
        assert resp.json()["severity"] == sev


@pytest.mark.asyncio
async def test_incident_filter_by_status(client: AsyncClient):
    for status in ["new", "investigating", "resolved", "new"]:
        await client.post(
            "/api/v1/incidents/",
            json={"title": f"Incident {status}", "severity": "medium"},
        )
        if status != "new":
            inc = (await client.get("/api/v1/incidents/")).json()["incidents"][-1]
            await client.put(
                f"/api/v1/incidents/{inc['id']}",
                json={"status": status},
            )

    new_resp = await client.get("/api/v1/incidents/?status=new")
    for inc in new_resp.json()["incidents"]:
        assert inc["status"] == "new"


@pytest.mark.asyncio
async def test_incident_filter_by_severity(client: AsyncClient):
    for sev in ["low", "medium", "high", "critical"]:
        await client.post(
            "/api/v1/incidents/",
            json={"title": f"Test {sev}", "severity": sev},
        )

    crit_resp = await client.get("/api/v1/incidents/?severity=critical")
    assert crit_resp.json()["total"] >= 1
    for inc in crit_resp.json()["incidents"]:
        assert inc["severity"] == "critical"


@pytest.mark.asyncio
async def test_incident_timeline_empty(client: AsyncClient):
    create_resp = await client.post(
        "/api/v1/incidents/",
        json={"title": "Empty Incident", "severity": "low"},
    )
    inc_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/incidents/{inc_id}/timeline")
    assert resp.status_code == 200
    body = resp.json()
    assert body["events"] == []
    assert body["iocs"] == []
    assert body["mitre_techniques"] == []
    assert body["response_actions"] == []
    assert body["ai_analyses"] == []


@pytest.mark.asyncio
async def test_incident_not_found_returns_404(client: AsyncClient):
    resp = await client.get(f"/api/v1/incidents/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_incident_update_nonexistent_returns_404(client: AsyncClient):
    resp = await client.put(
        f"/api/v1/incidents/{uuid.uuid4()}",
        json={"status": "resolved"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_incident_create_and_assign(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Phishing Campaign",
            "severity": "high",
            "assigned_to": str(test_user.id),
        },
    )
    assert resp.status_code == 201
    assert resp.json()["assigned_to"] == str(test_user.id)


@pytest.mark.asyncio
async def test_incident_pagination(client: AsyncClient):
    for i in range(8):
        await client.post(
            "/api/v1/incidents/",
            json={"title": f"Inc {i}", "severity": "info"},
        )

    page1 = await client.get("/api/v1/incidents/?page=1&page_size=3")
    assert len(page1.json()["incidents"]) == 3
    assert page1.json()["total"] >= 8
