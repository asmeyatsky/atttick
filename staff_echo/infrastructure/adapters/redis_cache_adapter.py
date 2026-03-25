from __future__ import annotations
"""Redis Cache Adapter — implements CachePort for production use."""

try:
    import redis.asyncio as aioredis

    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False


class RedisCacheAdapter:

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._client = None
        if _HAS_REDIS:
            self._client = aioredis.from_url(redis_url)

    async def get(self, key: str) -> str | None:
        if not self._client:
            return None
        value = await self._client.get(key)
        return value.decode("utf-8") if value else None

    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        if self._client:
            await self._client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        if self._client:
            await self._client.delete(key)
