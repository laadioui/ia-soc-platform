from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog
from opensearchpy import (
    AsyncHttpConnection,
    AsyncOpenSearch,
    NotFoundError,
    RequestError,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = structlog.get_logger()

DEFAULT_INDEX_PREFIX = "soc"

INDEX_MAPPINGS: dict[str, dict[str, Any]] = {
    "events": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "source_ip": {"type": "ip"},
                "destination_ip": {"type": "ip"},
                "event_type": {"type": "keyword"},
                "severity": {"type": "keyword"},
                "source": {"type": "keyword"},
                "message": {"type": "text"},
                "raw_log": {"type": "text"},
                "tags": {"type": "keyword"},
                "geo": {
                    "properties": {
                        "location": {"type": "geo_point"},
                        "country": {"type": "keyword"},
                    }
                },
                "enrichment": {"type": "object", "enabled": True},
            }
        },
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "index.lifecycle.name": "soc-policy",
        },
    },
    "alerts": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "alert_id": {"type": "keyword"},
                "rule_id": {"type": "keyword"},
                "rule_name": {"type": "text"},
                "severity": {"type": "keyword"},
                "status": {"type": "keyword"},
                "source_ip": {"type": "ip"},
                "destination_ip": {"type": "ip"},
                "description": {"type": "text"},
                "mitre_tactic": {"type": "keyword"},
                "mitre_technique": {"type": "keyword"},
                "tags": {"type": "keyword"},
            }
        },
        "settings": {"number_of_shards": 2, "number_of_replicas": 1},
    },
    "incidents": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "incident_id": {"type": "keyword"},
                "title": {"type": "text"},
                "description": {"type": "text"},
                "severity": {"type": "keyword"},
                "status": {"type": "keyword"},
                "assigned_to": {"type": "keyword"},
                "related_alerts": {"type": "keyword"},
                "tags": {"type": "keyword"},
            }
        },
        "settings": {"number_of_shards": 2, "number_of_replicas": 1},
    },
    "threat_intel": {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "ioc_type": {"type": "keyword"},
                "ioc_value": {"type": "keyword"},
                "threat_type": {"type": "keyword"},
                "confidence": {"type": "float"},
                "source": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "description": {"type": "text"},
            }
        },
        "settings": {"number_of_shards": 1, "number_of_replicas": 1},
    },
}


class OpenSearchClient:
    """Async OpenSearch client for indexing and searching security events."""

    def __init__(self) -> None:
        self._client: AsyncOpenSearch | None = None

    def _build_client(self) -> AsyncOpenSearch:
        hosts = settings.OPENSEARCH_URL.split(",")
        return AsyncOpenSearch(
            hosts=hosts,
            connection_class=AsyncHttpConnection,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_fingerprint=False,
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def start(self) -> None:
        self._client = self._build_client()
        if not await self._client.ping():
            raise ConnectionError("OpenSearch ping failed")
        await self._ensure_indices()
        logger.info("opensearch_client_started", url=settings.OPENSEARCH_URL)

    async def stop(self) -> None:
        if self._client is not None:
            await self._client.close()
            logger.info("opensearch_client_stopped")

    def _get_client(self) -> AsyncOpenSearch:
        if self._client is None:
            raise RuntimeError("OpenSearchClient is not started. Call start() first.")
        return self._client

    async def _ensure_indices(self) -> None:
        client = self._get_client()
        for index_name, config in INDEX_MAPPINGS.items():
            full_index = f"{DEFAULT_INDEX_PREFIX}-{index_name}"
            exists = await client.indices.exists(index=full_index)
            if not exists:
                await client.indices.create(index=full_index, body=config)
                logger.info("opensearch_index_created", index=full_index)

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=5),
        reraise=True,
    )
    async def index_event(
        self,
        index: str,
        document: dict[str, Any],
        doc_id: str | None = None,
    ) -> dict[str, Any]:
        client = self._get_client()
        full_index = f"{DEFAULT_INDEX_PREFIX}-{index}"

        if "timestamp" not in document:
            document["timestamp"] = datetime.now(UTC).isoformat()

        try:
            result = await client.index(
                index=full_index,
                body=document,
                id=doc_id,
                refresh="wait_for",
            )
            logger.debug(
                "opensearch_document_indexed",
                index=full_index,
                doc_id=result.get("_id"),
            )
            return result
        except RequestError as exc:
            logger.error("opensearch_index_error", index=full_index, error=str(exc))
            raise

    async def index_events(self, documents: list[dict[str, Any]], index: str = "events") -> dict[str, Any]:
        client = self._get_client()
        full_index = f"{DEFAULT_INDEX_PREFIX}-{index}"

        now = datetime.now(UTC).isoformat()
        for doc in documents:
            if "timestamp" not in doc:
                doc["timestamp"] = now

        bulk_body = []
        for doc in documents:
            bulk_body.append({"index": {"_index": full_index}})
            bulk_body.append(doc)

        result = await client.bulk(body=bulk_body, refresh="wait_for")
        errors = result.get("errors", False)
        if errors:
            logger.warning("opensearch_bulk_index_errors", index=full_index, result=result)
        else:
            logger.info("opensearch_bulk_indexed", index=full_index, count=len(documents))
        return result

    async def search(
        self,
        index: str,
        query: dict[str, Any],
        size: int = 50,
        from_: int = 0,
        sort: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        client = self._get_client()
        full_index = f"{DEFAULT_INDEX_PREFIX}-{index}"

        body: dict[str, Any] = {
            "query": query,
            "size": size,
            "from": from_,
        }
        if sort:
            body["sort"] = sort

        try:
            result = await client.search(index=full_index, body=body)
            return result
        except NotFoundError:
            logger.warning("opensearch_index_not_found", index=full_index)
            return {"hits": {"hits": [], "total": {"value": 0}}}

    async def get_document(self, index: str, doc_id: str) -> dict[str, Any] | None:
        client = self._get_client()
        full_index = f"{DEFAULT_INDEX_PREFIX}-{index}"

        try:
            result = await client.get(index=full_index, id=doc_id)
            return result
        except NotFoundError:
            return None

    async def delete_document(self, index: str, doc_id: str) -> bool:
        client = self._get_client()
        full_index = f"{DEFAULT_INDEX_PREFIX}-{index}"

        try:
            await client.delete(index=full_index, id=doc_id)
            return True
        except NotFoundError:
            return False

    async def update_document(self, index: str, doc_id: str, body: dict[str, Any]) -> bool:
        client = self._get_client()
        full_index = f"{DEFAULT_INDEX_PREFIX}-{index}"

        try:
            await client.update(index=full_index, id=doc_id, body={"doc": body})
            return True
        except NotFoundError:
            return False

    async def health_check(self) -> dict[str, Any]:
        client = self._get_client()
        try:
            info = await client.info()
            return {"status": "healthy", "cluster_name": info.get("cluster_name", "unknown")}
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}


opensearch_client = OpenSearchClient()
