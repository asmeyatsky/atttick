"""
Domain Tests — Pricing Validation Service

Tests the accuracy guardrail business rules:
- No pricing mentioned -> valid
- Known pricing -> valid
- Unknown pricing -> requires handoff
- Price lower than source -> invalid + handoff
"""

from staff_echo.domain.services.pricing_validation_service import PricingValidationService
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource


class TestPricingValidationService:

    def setup_method(self):
        self.service = PricingValidationService()
        self.known_pricing = [
            PricingInfo(amount=99.00, currency="USD", product_id="basic", source=PricingSource.BIGQUERY_VERIFIED),
            PricingInfo(amount=199.00, currency="USD", product_id="pro", source=PricingSource.BIGQUERY_VERIFIED),
        ]

    def test_no_pricing_mentioned(self):
        result = self.service.validate_pricing_response(
            "We have great products available!", self.known_pricing
        )
        assert result.is_valid
        assert not result.requires_handoff

    def test_valid_known_pricing(self):
        result = self.service.validate_pricing_response(
            "Our basic plan is $99.00 per month.", self.known_pricing
        )
        assert result.is_valid
        assert not result.requires_handoff

    def test_unknown_price_requires_handoff(self):
        result = self.service.validate_pricing_response(
            "That service costs $49.99.", self.known_pricing
        )
        assert not result.is_valid
        assert result.requires_handoff

    def test_price_lower_than_source_is_invalid(self):
        result = self.service.validate_pricing_response(
            "I can offer the basic plan for $79.00.", self.known_pricing
        )
        assert not result.is_valid
        assert result.requires_handoff
        assert "lower than source" in result.reason

    def test_no_verified_pricing_data(self):
        result = self.service.validate_pricing_response(
            "The price is $50.00.", []
        )
        assert not result.is_valid
        assert result.requires_handoff
        assert "no verified pricing" in result.reason.lower()
