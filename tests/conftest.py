from __future__ import annotations

import asyncio
import os
import sys

# Tests run on an in-memory SQLite database regardless of the .env content
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
# Disable rate limiting during tests
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000000"
os.environ["RATE_LIMIT_LOGIN_PER_MINUTE"] = "1000000"
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event as sa_event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

ROOT = str(__import__("pathlib").Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SERVICES_DIR = str(__import__("pathlib").Path(ROOT) / "services" / "collector-service")
if SERVICES_DIR not in sys.path:
    sys.path.insert(0, SERVICES_DIR)

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.event import SecurityEvent
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.detection_rule import DetectionRule
from app.models.ioc import IOC
from app.models.mitre import MITRETechnique
from app.models.threat_intelligence import ThreatIntelligence
from app.core.security import hash_password


# ---------------------------------------------------------------------------
# Event-loop fixture (single loop for entire session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Async SQLite engine & tables (per-test)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# Override FastAPI dependency to use test DB
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Pre-populated test user
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="analyst@example.com",
        username="analyst1",
        full_name="Test Analyst",
        hashed_password=hash_password("StrongPass123!"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        username="admin1",
        full_name="Test Admin",
        hashed_password=hash_password("AdminPass123!"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    from app.core.security import create_access_token

    token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(test_admin: User) -> dict[str, str]:
    from app.core.security import create_access_token

    token = create_access_token({"sub": str(test_admin.id), "username": test_admin.username})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Pre-populated test event
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_event(db_session: AsyncSession) -> SecurityEvent:
    event = SecurityEvent(
        id=uuid.uuid4(),
        event_id=f"evt-{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(timezone.utc),
        source="linux-syslog",
        source_type="server",
        category="authentication",
        action="login_failed",
        severity="medium",
        user_name="admin",
        source_ip="192.168.1.50",
        destination_ip="10.0.0.5",
        destination_port=22,
        hostname="webserver-01",
        is_alert=False,
        processed=False,
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event


# ---------------------------------------------------------------------------
# Mock Kafka producer
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_kafka_producer():
    producer = MagicMock()
    producer.produce = MagicMock()
    producer.poll = MagicMock()
    producer.flush = MagicMock()
    return producer
