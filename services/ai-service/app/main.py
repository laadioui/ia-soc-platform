from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import make_asgi_app

from app.config import settings

logger = structlog.get_logger()
router = APIRouter()
metrics_app = make_asgi_app()


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting AI Service", version=settings.APP_VERSION)
    from app.rag.embeddings import embedding_service
    from app.rag.retriever import retriever

    await embedding_service.start()
    await retriever.start()
    yield
    logger.info("Shutting down AI Service")
    await retriever.stop()
    await embedding_service.stop()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered security analysis service with RAG and embeddings",
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

app.mount("/metrics", metrics_app)
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# ── Request / Response models ─────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    event_data: dict[str, Any] = Field(..., description="Raw event data to analyze")
    context: str | None = Field(None, description="Optional additional context")


class AnalyzeResponse(BaseModel):
    analysis: str
    severity_assessment: str
    recommended_actions: list[str]
    mitre_mapping: dict[str, str] | None = None
    confidence: float
    processing_time_ms: float


class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Text to summarize", min_length=10)
    max_length: int | None = Field(None, description="Max summary length in words")


class SummarizeResponse(BaseModel):
    summary: str
    key_points: list[str]
    processing_time_ms: float


class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to generate embedding for")
    model: str | None = Field(None, description="Override embedding model")


class EmbeddingResponse(BaseModel):
    embedding: list[float]
    dimension: int
    model: str
    processing_time_ms: float


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    index: str = Field("events", description="Index to search")
    top_k: int = Field(5, ge=1, le=50)
    filters: dict[str, Any] | None = Field(None, description="Optional filters")


class SearchResult(BaseModel):
    id: str
    score: float
    source: dict[str, Any]
    highlights: dict[str, list[str]] | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    query_time_ms: float


# ── Endpoints ─────────────────────────────────────────────────────────


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_event(request: AnalyzeRequest):
    start_time = time.time()

    try:
        from app.rag.generator import LLMGenerator
        from app.rag.retriever import retriever

        generator = LLMGenerator()

        analysis = await generator.analyze_event(
            event_data=request.event_data,
            context=request.context,
        )

        await retriever.search_similar_events(
            query=str(request.event_data),
            top_k=3,
        )

        processing_time = (time.time() - start_time) * 1000

        return AnalyzeResponse(
            analysis=analysis.get("analysis", ""),
            severity_assessment=analysis.get("severity_assessment", "unknown"),
            recommended_actions=analysis.get("recommended_actions", []),
            mitre_mapping=analysis.get("mitre_mapping"),
            confidence=analysis.get("confidence", 0.0),
            processing_time_ms=round(processing_time, 2),
        )

    except Exception as exc:
        logger.error("analyze_event_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    start_time = time.time()

    try:
        from app.rag.generator import LLMGenerator

        generator = LLMGenerator()

        result = await generator.summarize(
            text=request.text,
            max_length=request.max_length,
        )

        processing_time = (time.time() - start_time) * 1000

        return SummarizeResponse(
            summary=result.get("summary", ""),
            key_points=result.get("key_points", []),
            processing_time_ms=round(processing_time, 2),
        )

    except Exception as exc:
        logger.error("summarize_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}")


@router.post("/embedding", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    start_time = time.time()

    try:
        from app.rag.embeddings import embedding_service

        embedding = await embedding_service.encode(request.text)

        processing_time = (time.time() - start_time) * 1000

        return EmbeddingResponse(
            embedding=embedding.tolist(),
            dimension=len(embedding),
            model=request.model or settings.EMBEDDING_MODEL,
            processing_time_ms=round(processing_time, 2),
        )

    except Exception as exc:
        logger.error("embedding_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {exc}")


@router.post("/search", response_model=SearchResponse)
async def search_similar(request: SearchRequest):
    start_time = time.time()

    try:
        from app.rag.retriever import retriever

        results = await retriever.search_similar_events(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )

        query_time = (time.time() - start_time) * 1000

        search_results = [
            SearchResult(
                id=r.get("id", ""),
                score=r.get("score", 0.0),
                source=r.get("source", {}),
                highlights=r.get("highlights"),
            )
            for r in results
        ]

        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query_time_ms=round(query_time, 2),
        )

    except Exception as exc:
        logger.error("search_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}")


@router.get("/health/llm")
async def llm_health():
    try:
        from app.rag.generator import LLMGenerator

        generator = LLMGenerator()
        is_healthy = await generator.health_check()
        return {"status": "healthy" if is_healthy else "unhealthy", "provider": "ollama", "model": settings.OLLAMA_MODEL}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}
