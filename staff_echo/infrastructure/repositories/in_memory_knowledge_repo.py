from __future__ import annotations
"""
In-memory Knowledge Repository — development/testing adapter.

Uses simple keyword matching for search. Production would use vector similarity.
"""

import asyncio

from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo


class InMemoryKnowledgeRepository:

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeEntry] = {}
        self._lock = asyncio.Lock()

    async def save(self, entry: KnowledgeEntry) -> None:
        async with self._lock:
            self._store[entry.id] = entry

    async def search(
        self,
        query: str,
        category: KnowledgeCategory | None = None,
        limit: int = 10,
    ) -> list[KnowledgeEntry]:
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results: list[tuple[float, KnowledgeEntry]] = []

        for entry in self._store.values():
            if category and entry.category != category:
                continue
            content_lower = entry.content.lower()
            matching_words = sum(1 for w in query_words if w in content_lower)
            if matching_words > 0:
                score = matching_words / max(len(query_words), 1)
                results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    async def get_pricing(self, product_id: str) -> list[PricingInfo]:
        pricing: list[PricingInfo] = []
        product_lower = product_id.lower()
        for entry in self._store.values():
            if entry.pricing_info and product_lower in entry.pricing_info.product_id.lower():
                pricing.append(entry.pricing_info)
        return pricing
