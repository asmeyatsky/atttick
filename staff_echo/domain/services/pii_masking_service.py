"""
PII Masking Domain Service

Architectural Intent:
- Assembles MaskedText from detected PII masks
- Detection is an infrastructure concern (PIIDetectorPort)
- This service owns the domain logic of HOW masking is applied
- Masks are applied in reverse order to preserve span positions
"""

from staff_echo.domain.value_objects.pii_mask import PIIMask, MaskedText


class PIIMaskingService:

    def mask_text(self, raw_text: str, detections: list[PIIMask]) -> MaskedText:
        sorted_masks = sorted(detections, key=lambda m: m.original_span[0], reverse=True)
        masked = raw_text
        for mask in sorted_masks:
            start, end = mask.original_span
            masked = masked[:start] + mask.replacement + masked[end:]
        return MaskedText(
            original_text=raw_text,
            masked_text=masked,
            masks=tuple(detections),
        )
