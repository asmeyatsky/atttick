from __future__ import annotations
"""
Pricing Info Value Object

Architectural Intent:
- Represents verified pricing data sourced from BigQuery or staff transcripts
- PricingSource tracks provenance for accuracy guardrails
- Business rule: UNVERIFIED pricing must never be quoted to customers
- Business rule: quoted price must never be lower than source data
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PricingSource(Enum):
    BIGQUERY_VERIFIED = "bigquery_verified"
    STAFF_TRANSCRIPT = "staff_transcript"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class PricingInfo:
    amount: float
    currency: str
    product_id: str
    source: PricingSource
    verified_at: datetime | None = None

    @property
    def has_verified_source(self) -> bool:
        return self.source in (
            PricingSource.BIGQUERY_VERIFIED,
            PricingSource.STAFF_TRANSCRIPT,
        )
