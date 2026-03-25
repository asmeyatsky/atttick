from __future__ import annotations
"""Cache Port — defines the contract for caching (FAQ responses, knowledge lookups)."""

from typing import Protocol


class CachePort(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None: ...
    async def delete(self, key: str) -> None: ...
