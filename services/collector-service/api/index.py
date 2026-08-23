"""Vercel serverless entry point.

The @vercel/python runtime detects the exported ASGI application and routes
requests to it. vercel.json maps every path (e.g. /api/v1/events, /health,
/docs) to this function so the FastAPI router keeps its original paths.

The serverless runtime does not reliably trigger the FastAPI lifespan, so the
database schema (and the demo dataset when SEED_DEMO_DATA is set) is prepared
at import time, i.e. once per cold start. The SQLite file lives in /tmp, the
only writable location on Vercel.
"""

import asyncio

from app.core.config import settings
from app.core.database import async_session, init_db
from app.services.demo_seed import seed_if_empty


async def _bootstrap() -> None:
    await init_db()
    if settings.SEED_DEMO_DATA:
        async with async_session() as session:
            await seed_if_empty(session)


asyncio.run(_bootstrap())

from app.main import app  # noqa: E402,F401 - exported for the Vercel runtime
