"""
Pricing Validation Domain Service

Architectural Intent:
- Enforces the PRD's accuracy guardrail: never hallucinate prices
- Validates that any price mentioned in AI responses exists in verified data
- If a price is lower than source data, it's flagged as invalid
- Unknown prices trigger human handoff rather than being guessed

Business Rules:
1. Prices in response must match known pricing data
2. Quoted price must never be LOWER than source (protects revenue)
3. If pricing query falls outside known data -> requires handoff
"""

import re
from dataclasses import dataclass

from staff_echo.domain.value_objects.pricing_info import PricingInfo


@dataclass(frozen=True)
class PricingValidationResult:
    is_valid: bool
    requires_handoff: bool
    reason: str


_PRICE_PATTERN = re.compile(r"\$[\d,]+(?:\.\d{2})?")


class PricingValidationService:

    def validate_pricing_response(
        self, response_text: str, known_pricing: list[PricingInfo]
    ) -> PricingValidationResult:
        mentioned_prices = _PRICE_PATTERN.findall(response_text)
        if not mentioned_prices:
            return PricingValidationResult(
                is_valid=True, requires_handoff=False, reason="No pricing mentioned"
            )

        known_amounts = {p.amount for p in known_pricing if p.has_verified_source}
        if not known_amounts:
            return PricingValidationResult(
                is_valid=False,
                requires_handoff=True,
                reason="Response mentions pricing but no verified pricing data available",
            )

        for price_str in mentioned_prices:
            amount = float(price_str.replace("$", "").replace(",", ""))
            if amount not in known_amounts:
                lower_than_source = any(amount < k for k in known_amounts)
                if lower_than_source:
                    return PricingValidationResult(
                        is_valid=False,
                        requires_handoff=True,
                        reason=f"Quoted price ${amount:.2f} is lower than source data",
                    )
                return PricingValidationResult(
                    is_valid=False,
                    requires_handoff=True,
                    reason=f"Price ${amount:.2f} not found in verified pricing data",
                )

        return PricingValidationResult(
            is_valid=True, requires_handoff=False, reason="All prices verified"
        )
