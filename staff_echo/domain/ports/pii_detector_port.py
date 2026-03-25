"""PII Detector Port — defines the contract for PII detection in text."""

from typing import Protocol

from staff_echo.domain.value_objects.pii_mask import PIIMask


class PIIDetectorPort(Protocol):
    def detect(self, text: str) -> list[PIIMask]: ...
