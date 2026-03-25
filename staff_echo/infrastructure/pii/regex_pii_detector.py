"""
Regex PII Detector — implements PIIDetectorPort.

Architectural Intent:
- Detects PII patterns using regular expressions
- Returns PIIMask value objects with span positions for domain masking service
- Covers: credit cards, emails, phones, SSNs per PRD requirements
"""

import re

from staff_echo.domain.value_objects.pii_mask import PIIMask, PIIType

_PATTERNS: list[tuple[PIIType, re.Pattern, str]] = [
    (
        PIIType.CREDIT_CARD,
        re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "[REDACTED_CC]",
    ),
    (
        PIIType.SSN,
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "[REDACTED_SSN]",
    ),
    (
        PIIType.EMAIL,
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    (
        PIIType.PHONE,
        re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "[REDACTED_PHONE]",
    ),
]


class RegexPIIDetector:

    def detect(self, text: str) -> list[PIIMask]:
        masks: list[PIIMask] = []
        for pii_type, pattern, replacement in _PATTERNS:
            for match in pattern.finditer(text):
                masks.append(
                    PIIMask(
                        original_span=(match.start(), match.end()),
                        pii_type=pii_type,
                        replacement=replacement,
                    )
                )
        masks.sort(key=lambda m: m.original_span[0])
        return masks
