"""
Tone Profile Value Object

Architectural Intent:
- Captures the linguistic fingerprint of staff communication style
- Extracted from approved transcripts during training data preparation
- Used to align AI-generated responses with the brand's human voice
- Formality levels map to distinct prompt engineering strategies
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToneProfile:
    greeting_style: str
    formality_level: str  # "casual", "professional", "formal"
    common_phrases: tuple[str, ...] = ()
    analogies: tuple[str, ...] = ()

    def matches_staff_voice(self, response_text: str) -> bool:
        text_lower = response_text.lower()
        if self.greeting_style and self.greeting_style.lower() in text_lower:
            return True
        matches = sum(
            1 for phrase in self.common_phrases if phrase.lower() in text_lower
        )
        return matches >= 1
