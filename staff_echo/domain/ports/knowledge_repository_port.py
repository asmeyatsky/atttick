from __future__ import annotations
"""Knowledge Repository Port — defines the contract for knowledge base access."""

from typing import Protocol

from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo


class KnowledgeRepositoryPort(Protocol):
    async def save(self, entry: KnowledgeEntry) -> None: ...
    async def search(
        self, query: str, category: KnowledgeCategory | None = None, limit: int = 10
    ) -> list[KnowledgeEntry]: ...
    async def get_pricing(self, product_id: str) -> list[PricingInfo]: ...
