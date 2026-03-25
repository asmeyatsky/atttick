from __future__ import annotations
"""
Chat Response Workflow — DAG-based Orchestration

Architectural Intent:
- Orchestrates the multi-step process of generating a chat response
- Parallelizes independent operations: knowledge search, pricing lookup, cache check
- Sequential steps only where data dependencies exist
- Implements accuracy guardrails: pricing validation triggers handoff

Parallelization Strategy:
  [Parallel] knowledge_search + pricing_lookup + cache_check
       |                |               |
       v                v               v
  [Sequential] build_context (merges parallel results)
       |
       v
  [Sequential] generate_response (AI with tone alignment)
       |
       v
  [Sequential] validate_pricing (guardrail check)
       |
       v
  WorkflowResult (response or handoff)
"""

import asyncio
import json
from dataclasses import dataclass, field

from staff_echo.domain.entities.knowledge_entry import KnowledgeCategory
from staff_echo.domain.ports.knowledge_repository_port import KnowledgeRepositoryPort
from staff_echo.domain.ports.ai_provider_port import AIProviderPort
from staff_echo.domain.ports.cache_port import CachePort
from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.services.pricing_validation_service import PricingValidationService
from staff_echo.domain.value_objects.message_content import MessageContent
from staff_echo.domain.value_objects.tone_profile import ToneProfile
from staff_echo.domain.value_objects.pricing_info import PricingInfo


@dataclass(frozen=True)
class WorkflowResult:
    response_text: str
    sources: tuple[str, ...] = ()
    is_verified: bool = False
    requires_handoff: bool = False
    handoff_reason: str = ""


class ChatResponseWorkflow:
    """
    DAG-based orchestration for generating a chat response.
    Parallelizes independent IO operations, serializes dependent logic.
    """

    def __init__(
        self,
        knowledge_repo: KnowledgeRepositoryPort,
        ai_provider: AIProviderPort,
        cache: CachePort,
        tone_service: ToneAlignmentService,
        pricing_service: PricingValidationService,
    ):
        self._knowledge_repo = knowledge_repo
        self._ai_provider = ai_provider
        self._cache = cache
        self._tone_service = tone_service
        self._pricing_service = pricing_service

    async def execute(
        self,
        messages: list[MessageContent],
        user_query: str,
        tone_profile: ToneProfile | None = None,
    ) -> WorkflowResult:
        # Phase 1: Parallel — knowledge search, pricing lookup, cache check
        knowledge_task = self._search_knowledge(user_query)
        pricing_task = self._lookup_pricing(user_query)
        cache_task = self._check_cache(user_query)

        knowledge_entries, pricing_data, cached_response = await asyncio.gather(
            knowledge_task, pricing_task, cache_task
        )

        # Phase 1.5: Return cached response if available
        if cached_response:
            return WorkflowResult(
                response_text=cached_response,
                sources=("cache",),
                is_verified=True,
            )

        # Phase 2: Sequential — build context from parallel results
        context = self._build_context(knowledge_entries, pricing_data)
        sources = tuple(e.id for e in knowledge_entries)
        is_verified = any(
            e.has_verified_pricing for e in knowledge_entries if e.is_pricing
        )

        # Phase 3: Sequential — generate AI response
        raw_response = await self._ai_provider.generate_response_full(
            messages=messages, context=context, tone_profile=tone_profile
        )

        # Phase 3.5: Tone alignment
        if tone_profile:
            raw_response = self._tone_service.align_response(raw_response, tone_profile)

        # Phase 4: Sequential — validate pricing
        validation = self._pricing_service.validate_pricing_response(
            raw_response, pricing_data
        )

        if not validation.is_valid or validation.requires_handoff:
            return WorkflowResult(
                response_text=raw_response,
                sources=sources,
                is_verified=False,
                requires_handoff=True,
                handoff_reason=validation.reason,
            )

        # Cache successful response
        await self._cache.set(
            f"chat:{user_query}", raw_response, ttl_seconds=1800
        )

        return WorkflowResult(
            response_text=raw_response,
            sources=sources,
            is_verified=is_verified,
        )

    async def _search_knowledge(self, query: str):
        from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry

        return await self._knowledge_repo.search(query, limit=5)

    async def _lookup_pricing(self, query: str) -> list[PricingInfo]:
        words = query.lower().split()
        all_pricing: list[PricingInfo] = []
        for word in words:
            if len(word) > 3:
                pricing = await self._knowledge_repo.get_pricing(word)
                all_pricing.extend(pricing)
        return all_pricing

    async def _check_cache(self, query: str) -> str | None:
        return await self._cache.get(f"chat:{query}")

    def _build_context(self, knowledge_entries, pricing_data) -> str:
        parts = []
        if knowledge_entries:
            parts.append("Relevant knowledge:")
            for entry in knowledge_entries:
                parts.append(f"- [{entry.category.value}] {entry.content}")
        if pricing_data:
            parts.append("\nVerified pricing:")
            for p in pricing_data:
                parts.append(f"- {p.product_id}: ${p.amount:.2f} {p.currency} (source: {p.source.value})")
        if not parts:
            parts.append("No specific knowledge found for this query.")
        return "\n".join(parts)
