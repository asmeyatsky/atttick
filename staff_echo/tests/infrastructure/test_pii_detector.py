"""
Infrastructure Tests — Regex PII Detector

Tests PII detection patterns for credit cards, emails, phones, SSNs.
"""

from staff_echo.infrastructure.pii.regex_pii_detector import RegexPIIDetector
from staff_echo.domain.value_objects.pii_mask import PIIType


class TestRegexPIIDetector:

    def setup_method(self):
        self.detector = RegexPIIDetector()

    def test_detect_credit_card(self):
        text = "My card is 4111-1111-1111-1111 thanks"
        masks = self.detector.detect(text)
        assert len(masks) >= 1
        cc_masks = [m for m in masks if m.pii_type == PIIType.CREDIT_CARD]
        assert len(cc_masks) == 1
        assert cc_masks[0].replacement == "[REDACTED_CC]"

    def test_detect_email(self):
        text = "Send it to user@example.com please"
        masks = self.detector.detect(text)
        email_masks = [m for m in masks if m.pii_type == PIIType.EMAIL]
        assert len(email_masks) == 1
        assert email_masks[0].replacement == "[REDACTED_EMAIL]"

    def test_detect_phone(self):
        text = "Call me at (555) 123-4567"
        masks = self.detector.detect(text)
        phone_masks = [m for m in masks if m.pii_type == PIIType.PHONE]
        assert len(phone_masks) == 1

    def test_detect_ssn(self):
        text = "SSN is 123-45-6789"
        masks = self.detector.detect(text)
        ssn_masks = [m for m in masks if m.pii_type == PIIType.SSN]
        assert len(ssn_masks) == 1

    def test_no_pii(self):
        text = "Just a normal sentence with no sensitive data."
        masks = self.detector.detect(text)
        assert len(masks) == 0

    def test_multiple_pii_types(self):
        text = "Email: a@b.com, Card: 4111-1111-1111-1111, SSN: 123-45-6789"
        masks = self.detector.detect(text)
        types = {m.pii_type for m in masks}
        assert PIIType.EMAIL in types
        assert PIIType.CREDIT_CARD in types
        assert PIIType.SSN in types

    def test_spans_are_correct(self):
        text = "Email: user@test.com"
        masks = self.detector.detect(text)
        email_mask = next(m for m in masks if m.pii_type == PIIType.EMAIL)
        start, end = email_mask.original_span
        assert text[start:end] == "user@test.com"
