from __future__ import annotations

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Text embedding service using sentence-transformers."""

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=5, max=30),
        reraise=True,
    )
    async def start(self) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        self._model = await loop.run_in_executor(
            None,
            lambda: SentenceTransformer(settings.EMBEDDING_MODEL),
        )
        logger.info(
            "embedding_service_started",
            model=settings.EMBEDDING_MODEL,
            dimension=settings.EMBEDDING_DIMENSION,
        )

    async def stop(self) -> None:
        self._model = None
        logger.info("embedding_service_stopped")

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            raise RuntimeError("EmbeddingService is not started. Call start() first.")
        return self._model

    async def encode(self, text: str) -> np.ndarray:
        model = self._get_model()

        import asyncio

        embedding = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.encode(text, normalize_embeddings=True, show_progress_bar=False),
        )
        return embedding

    async def encode_batch(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        model = self._get_model()

        import asyncio

        embeddings = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=batch_size,
            ),
        )
        return embeddings

    def get_dimension(self) -> int:
        model = self._get_model()
        return model.get_sentence_embedding_dimension()


embedding_service = EmbeddingService()
