"""Redis cache for dress advice."""

import logging

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisAdviceCache:
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self._url = redis_url
        self._ttl = default_ttl
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> str | None:
        try:
            client = await self._get_client()
            return await client.get(key)
        except Exception:
            return None

    async def set(self, key: str, text: str, ttl_seconds: int | None = None) -> None:
        try:
            client = await self._get_client()
            await client.set(key, text, ex=ttl_seconds or self._ttl)
        except Exception as e:
            logger.warning("Redis advice cache set failed key=%s: %s", key, e)
