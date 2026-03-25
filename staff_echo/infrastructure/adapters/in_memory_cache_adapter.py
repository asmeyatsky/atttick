from __future__ import annotations
"""In-memory Cache Adapter — implements CachePort for development/testing."""

import time


class InMemoryCacheAdapter:

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        self._store[key] = (value, time.time() + ttl_seconds)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)
