from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import async_session, engine, init_db
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from app.services.demo_seed import seed_if_empty

logger = structlog.get_logger()

metrics_app = make_asgi_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI SOC Platform API", version=settings.APP_VERSION)
    await init_db()
    if settings.SEED_DEMO_DATA:
        async with async_session() as session:
            await seed_if_empty(session)
    yield
    logger.info("Shutting down AI SOC Platform API")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Security Operations Center Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.mount("/metrics", metrics_app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-soc-backend", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
