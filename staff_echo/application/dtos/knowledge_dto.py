from __future__ import annotations
"""
Knowledge DTOs

Architectural Intent:
- Data transfer objects for knowledge retrieval and search
- PricingDTO surfaces verified pricing status for source citation badges
"""

from pydantic import BaseModel


class PricingDTO(BaseModel):
    amount: float
    currency: str
    product_id: str
    source: str
    is_verified: bool


class KnowledgeEntryDTO(BaseModel):
    id: str
    category: str
    content: str
    relevance_score: float = 0.0
    pricing: PricingDTO | None = None


class SearchKnowledgeRequest(BaseModel):
    query: str
    category: str | None = None
    limit: int = 10
