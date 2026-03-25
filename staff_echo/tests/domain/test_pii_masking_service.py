"""
Domain Tests — PII Masking Service

Tests the domain logic for assembling masked text from detected PII.
"""

from staff_echo.domain.services.pii_masking_service import PIIMaskingService
from staff_echo.domain.value_objects.pii_mask import PIIMask, PIIType


class TestPIIMaskingService:

    def setup_method(self):
        self.service = PIIMaskingService()

    def test_mask_single_pii(self):
        detections = [
            PIIMask(original_span=(10, 22), pii_type=PIIType.EMAIL, replacement="[REDACTED_EMAIL]")
        ]
        result = self.service.mask_text("Contact: test@email.com for info", detections)

        assert "[REDACTED_EMAIL]" in result.masked_text
        assert result.has_pii
        assert result.mask_count == 1
        assert result.original_text == "Contact: test@email.com for info"

    def test_mask_multiple_pii(self):
        text = "CC: 4111-1111-1111-1111, email: user@test.com"
        detections = [
            PIIMask(original_span=(4, 23), pii_type=PIIType.CREDIT_CARD, replacement="[REDACTED_CC]"),
            PIIMask(original_span=(32, 45), pii_type=PIIType.EMAIL, replacement="[REDACTED_EMAIL]"),
        ]
        result = self.service.mask_text(text, detections)

        assert "[REDACTED_CC]" in result.masked_text
        assert "[REDACTED_EMAIL]" in result.masked_text
        assert result.mask_count == 2

    def test_no_detections(self):
        result = self.service.mask_text("Clean text with no PII", [])
        assert result.masked_text == "Clean text with no PII"
        assert not result.has_pii
        assert result.mask_count == 0
