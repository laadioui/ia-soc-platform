from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient


# ── Register ──────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "newuser@example.com"
    assert body["username"] == "newuser"
    assert "id" in body


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "username": "unique_name",
            "password": "SecurePass123!",
        },
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "different@example.com",
            "username": "analyst1",
            "password": "SecurePass123!",
        },
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "123",
        },
    )
    assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "analyst1", "password": "StrongPass123!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "analyst1", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "ghost", "password": "Whatever123!"},
    )
    assert resp.status_code == 401


# ── Token Refresh ─────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, test_user):
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "analyst1", "password": "StrongPass123!"},
    )
    refresh_token = login.json()["refresh_token"]

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_token_refresh_invalid(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "garbage.token.value"},
    )
    assert resp.status_code == 401


# ── Change Password ──────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user, auth_headers):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "StrongPass123!",
            "new_password": "NewStrongPass456!",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "analyst1", "password": "NewStrongPass456!"},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, test_user, auth_headers):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "WrongOldPass!",
            "new_password": "NewStrongPass456!",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


# ── Invalid credentials edge cases ───────────────────────────────────────
@pytest.mark.asyncio
async def test_login_empty_body(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "username": "someuser",
            "password": "SecurePass123!",
        },
    )
    assert resp.status_code == 422
