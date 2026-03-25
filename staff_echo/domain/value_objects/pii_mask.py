"""
PII Mask Value Objects

Architectural Intent:
- Represents detected PII and the masking applied to protect customer data
- PIIMask captures individual detection results with span positions
- MaskedText is the final result after all PII has been redacted
- Required by PRD: auto-redact credit cards, addresses before LLM training
"""

from dataclasses import dataclass
from enum import Enum


class PIIType(Enum):
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    SSN = "ssn"
    NAME = "name"


@dataclass(frozen=True)
class PIIMask:
    original_span: tuple[int, int]
    pii_type: PIIType
    replacement: str


@dataclass(frozen=True)
class MaskedText:
    original_text: str
    masked_text: str
    masks: tuple[PIIMask, ...]

    @property
    def mask_count(self) -> int:
        return len(self.masks)

    @property
    def has_pii(self) -> bool:
        return len(self.masks) > 0
