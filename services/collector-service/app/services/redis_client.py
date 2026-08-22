from __future__ import annotations

import time
from typing import Any

import structlog
from redis.asyncio import ConnectionPool, Redis
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = structlog.get_logger()


class RedisClient:
    """Async Redis client for caching and rate limiting."""

    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def start(self) -> None:
        self._pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        self._client = Redis(connection_pool=self._pool)
        await self._client.ping()
        logger.info("redis_client_started", url=settings.REDIS_URL)

    async def stop(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            logger.info("redis_client_stopped")
        if self._pool is not None:
            await self._pool.disconnect()

    def _get_client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("RedisClient is not started. Call start() first.")
        return self._client

    async def health_check(self) -> dict[str, Any]:
        client = self._get_client()
        try:
            await client.ping()
            info = await client.info("memory")
            return {
                "status": "healthy",
                "used_memory_human": info.get("used_memory_human", "unknown"),
            }
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}

    # ── Caching ────────────────────────────────────────────────────────

    async def cache_get(self, key: str) -> Any | None:
        client = self._get_client()
        value = await client.get(key)
        if value is None:
            return None
        logger.debug("cache_hit", key=key)
        return value

    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
    ) -> None:
        client = self._get_client()
        await client.setex(key, ttl_seconds, value)
        logger.debug("cache_set", key=key, ttl=ttl_seconds)

    async def cache_delete(self, key: str) -> bool:
        client = self._get_client()
        deleted = await client.delete(key)
        return deleted > 0

    async def cache_exists(self, key: str) -> bool:
        client = self._get_client()
        return bool(await client.exists(key))

    async def cache_increment(self, key: str, amount: int = 1, ttl_seconds: int | None = None) -> int:
        client = self._get_client()
        value = await client.incrby(key, amount)
        if ttl_seconds is not None:
            await client.expire(key, ttl_seconds)
        return value

    # ── Rate Limiting ──────────────────────────────────────────────────

    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int | None = None,
        window_seconds: int = 60,
    ) -> tuple[bool, dict[str, int]]:
        client = self._get_client()
        limit = max_requests or settings.RATE_LIMIT_PER_MINUTE
        key = f"rate_limit:{identifier}"

        now = time.time()
        window_start = now - window_seconds

        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds)
        results = await pipe.execute()

        current_count = results[2]
        remaining = max(0, limit - current_count)
        allowed = current_count <= limit

        headers = {
            "X-RateLimit-Limit": limit,
            "X-RateLimit-Remaining": remaining,
            "X-RateLimit-Reset": int(now + window_seconds),
        }

        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                identifier=identifier,
                count=current_count,
                limit=limit,
            )
        else:
            logger.debug(
                "rate_limit_check",
                identifier=identifier,
                count=current_count,
                limit=limit,
            )

        return allowed, headers

    async def check_login_rate_limit(
        self,
        identifier: str,
        max_requests: int | None = None,
        window_seconds: int = 60,
    ) -> tuple[bool, dict[str, int]]:
        limit = max_requests or settings.RATE_LIMIT_LOGIN_PER_MINUTE
        return await self.check_rate_limit(
            identifier=f"login:{identifier}",
            max_requests=limit,
            window_seconds=window_seconds,
        )

    # ── Sets / Sorted Sets for lists ──────────────────────────────────

    async def add_to_set(self, key: str, *values: str) -> int:
        client = self._get_client()
        return await client.sadd(key, *values)

    async def get_set_members(self, key: str) -> set[str]:
        client = self._get_client()
        return await client.smembers(key)

    async def remove_from_set(self, key: str, *values: str) -> int:
        client = self._get_client()
        return await client.srem(key, *values)

    # ── Pub/Sub helpers ───────────────────────────────────────────────

    async def publish(self, channel: str, message: str) -> int:
        client = self._get_client()
        return await client.publish(channel, message)

    async def subscribe(self, *channels: str):
        client = self._get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub

    # ── Locking ────────────────────────────────────────────────────────

    async def acquire_lock(
        self,
        lock_key: str,
        timeout_seconds: int = 10,
        blocking_timeout: int = 5,
    ) -> bool:
        client = self._get_client()
        lock = client.lock(
            f"lock:{lock_key}",
            timeout=timeout_seconds,
            blocking_timeout=blocking_timeout,
        )
        return await lock.acquire()

    async def release_lock(self, lock_key: str) -> None:
        client = self._get_client()
        lock = client.lock(f"lock:{lock_key}")
        try:
            await lock.release()
        except Exception:
            pass


redis_client = RedisClient()
