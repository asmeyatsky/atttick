from __future__ import annotations
"""
Knowledge Entry Entity

Architectural Intent:
- Represents a retrievable piece of knowledge extracted from staff data
- Categories map to PRD requirements: product specs, pricing, FAQs
- Pricing entries carry PricingInfo for accuracy guardrail validation
- Relevance score used for RAG-style retrieval ranking
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum

from staff_echo.domain.value_objects.pricing_info import PricingInfo


class KnowledgeCategory(Enum):
    PRODUCT_SPEC = "product_spec"
    PRICING = "pricing"
    FAQ = "faq"
    GENERAL = "general"


@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    category: KnowledgeCategory
    content: str
    source_transcript_id: str | None = None
    pricing_info: PricingInfo | None = None
    relevance_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_pricing(self) -> bool:
        return self.category == KnowledgeCategory.PRICING

    @property
    def has_verified_pricing(self) -> bool:
        return (
            self.pricing_info is not None
            and self.pricing_info.has_verified_source
        )
