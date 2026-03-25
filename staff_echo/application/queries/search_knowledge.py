"""Search Knowledge Query — retrieves relevant knowledge entries with caching."""

from staff_echo.domain.entities.knowledge_entry import KnowledgeCategory
from staff_echo.domain.ports.knowledge_repository_port import KnowledgeRepositoryPort
from staff_echo.domain.ports.cache_port import CachePort
from staff_echo.application.dtos.knowledge_dto import (
    SearchKnowledgeRequest,
    KnowledgeEntryDTO,
    PricingDTO,
)

import json


class SearchKnowledgeQuery:

    def __init__(
        self,
        knowledge_repo: KnowledgeRepositoryPort,
        cache: CachePort,
    ):
        self._knowledge_repo = knowledge_repo
        self._cache = cache

    async def execute(self, request: SearchKnowledgeRequest) -> list[KnowledgeEntryDTO]:
        cache_key = f"knowledge:{request.query}:{request.category}:{request.limit}"
        cached = await self._cache.get(cache_key)
        if cached:
            return [KnowledgeEntryDTO.model_validate_json(c) for c in json.loads(cached)]

        category = KnowledgeCategory(request.category) if request.category else None
        entries = await self._knowledge_repo.search(
            query=request.query, category=category, limit=request.limit
        )

        dtos = []
        for entry in entries:
            pricing_dto = None
            if entry.pricing_info:
                pricing_dto = PricingDTO(
                    amount=entry.pricing_info.amount,
                    currency=entry.pricing_info.currency,
                    product_id=entry.pricing_info.product_id,
                    source=entry.pricing_info.source.value,
                    is_verified=entry.pricing_info.has_verified_source,
                )
            dtos.append(
                KnowledgeEntryDTO(
                    id=entry.id,
                    category=entry.category.value,
                    content=entry.content,
                    relevance_score=entry.relevance_score,
                    pricing=pricing_dto,
                )
            )

        await self._cache.set(
            cache_key,
            json.dumps([d.model_dump_json() for d in dtos]),
            ttl_seconds=1800,
        )
        return dtos
