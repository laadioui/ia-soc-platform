from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.rag.embeddings import embedding_service

logger = structlog.get_logger()

_search_indices = {
    "events": "soc_events",
    "alerts": "soc_alerts",
    "incidents": "soc_incidents",
    "threat_intel": "soc_threat_intel",
}


class Retriever:
    """RAG retriever that searches pgvector for similar incidents/events."""

    def __init__(self) -> None:
        self._engine = None
        self._session_factory: async_sessionmaker | None = None

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        reraise=True,
    )
    async def start(self) -> None:
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=10,
            max_overflow=5,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        await self._ensure_vector_extension()
        logger.info("retriever_started")

    async def stop(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            logger.info("retriever_stopped")

    def _get_session_factory(self) -> async_sessionmaker:
        if self._session_factory is None:
            raise RuntimeError("Retriever is not started. Call start() first.")
        return self._session_factory

    async def _ensure_vector_extension(self) -> None:
        factory = self._get_session_factory()
        async with factory() as session:
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await session.commit()

    async def _ensure_embedding_column(self, table: str) -> None:
        factory = self._get_session_factory()
        async with factory() as session:
            await session.execute(
                text(
                    f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS embedding vector({settings.EMBEDDING_DIMENSION})"
                )
            )
            await session.commit()

    async def store_embedding(
        self,
        table: str,
        record_id: int | str,
        text_content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        factory = self._get_session_factory()

        embedding = await embedding_service.encode(text_content)

        import json

        embedding_list = embedding.tolist()

        async with factory() as session:
            query = text(
                f"""
                INSERT INTO {table} (id, content, embedding, metadata_json)
                VALUES (:id, :content, :embedding, :metadata)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata_json = EXCLUDED.metadata_json
                """
            )
            await session.execute(
                query,
                {
                    "id": record_id,
                    "content": text_content,
                    "embedding": str(embedding_list),
                    "metadata": json.dumps(metadata or {}),
                },
            )
            await session.commit()

        logger.debug("embedding_stored", table=table, id=record_id)

    async def search_similar_events(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
        threshold: float = 0.3,
    ) -> list[dict[str, Any]]:
        factory = self._get_session_factory()
        embedding = await embedding_service.encode(query)
        embedding_list = embedding.tolist()

        import json

        filter_clause = ""
        params: dict[str, Any] = {
            "embedding": str(embedding_list),
            "top_k": top_k,
            "threshold": threshold,
        }

        if filters:
            filter_parts = []
            for key, value in filters.items():
                if key in ("severity", "event_type", "status", "source"):
                    filter_parts.append(f"metadata_json->>'{key}' = :filter_{key}")
                    params[f"filter_{key}"] = value
            if filter_parts:
                filter_clause = "AND " + " AND ".join(filter_parts)

        query_sql = text(
            f"""
            SELECT
                id,
                1 - (embedding <=> :embedding::vector) AS score,
                content,
                metadata_json
            FROM soc_events
            WHERE 1 - (embedding <=> :embedding::vector) > :threshold
            {filter_clause}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
            """
        )

        async with factory() as session:
            result = await session.execute(query_sql, params)
            rows = result.fetchall()

        results = []
        for row in rows:
            meta = {}
            if row.metadata_json:
                try:
                    meta = json.loads(row.metadata_json) if isinstance(row.metadata_json, str) else row.metadata_json
                except (json.JSONDecodeError, TypeError):
                    meta = {}

            results.append(
                {
                    "id": str(row.id),
                    "score": float(row.score),
                    "source": {
                        "content": row.content,
                        **meta,
                    },
                }
            )

        logger.debug("search_completed", query_length=len(query), results_count=len(results))
        return results

    async def search_similar_incidents(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.3,
    ) -> list[dict[str, Any]]:
        factory = self._get_session_factory()
        embedding = await embedding_service.encode(query)
        embedding_list = embedding.tolist()

        import json

        query_sql = text(
            """
            SELECT
                id,
                1 - (embedding <=> :embedding::vector) AS score,
                title,
                description,
                severity,
                status,
                metadata_json
            FROM soc_incidents
            WHERE 1 - (embedding <=> :embedding::vector) > :threshold
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
            """
        )

        async with factory() as session:
            result = await session.execute(
                query_sql,
                {"embedding": str(embedding_list), "top_k": top_k, "threshold": threshold},
            )
            rows = result.fetchall()

        results = []
        for row in rows:
            results.append(
                {
                    "id": str(row.id),
                    "score": float(row.score),
                    "source": {
                        "title": row.title,
                        "description": row.description,
                        "severity": row.severity,
                        "status": row.status,
                    },
                }
            )

        return results

    async def get_context_for_generation(
        self,
        query: str,
        top_k: int = 3,
    ) -> str:
        results = await self.search_similar_events(query=query, top_k=top_k)

        if not results:
            return "No relevant historical context found."

        context_parts = []
        for i, result in enumerate(results, 1):
            source = result.get("source", {})
            score = result.get("score", 0)
            content = source.get("content", "N/A")
            context_parts.append(f"[{i}] (relevance: {score:.2f}) {content}")

        return "\n\n".join(context_parts)


retriever = Retriever()
