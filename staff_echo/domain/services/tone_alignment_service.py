"""
Tone Alignment Domain Service

Architectural Intent:
- Adjusts AI-generated responses to match staff communication style
- Applies greeting style, formality level, and common phrases
- Calculates a tone score measuring alignment with the staff voice
- Pure domain logic — no external dependencies

Key Design Decisions:
1. Greeting injection at response start if missing
2. Formality adjustment via word substitution
3. Score based on phrase match ratio
"""

from staff_echo.domain.value_objects.tone_profile import ToneProfile

_CASUAL_SUBSTITUTIONS = {
    "I would like to inform you": "Just letting you know",
    "Please be advised": "Heads up",
    "We regret to inform you": "Unfortunately",
    "At your earliest convenience": "When you get a chance",
}

_FORMAL_SUBSTITUTIONS = {
    "hey": "Hello",
    "yeah": "Yes",
    "gonna": "going to",
    "wanna": "want to",
    "no problem": "You are welcome",
}


class ToneAlignmentService:

    def align_response(self, raw_response: str, tone_profile: ToneProfile) -> str:
        result = raw_response
        if tone_profile.greeting_style and not result.lower().startswith(
            tone_profile.greeting_style.lower().split()[0]
        ):
            first_sentence_end = result.find(".")
            if first_sentence_end > 0 and first_sentence_end < 100:
                result = f"{tone_profile.greeting_style} {result}"
            else:
                result = f"{tone_profile.greeting_style} {result}"

        if tone_profile.formality_level == "casual":
            for formal, casual in _CASUAL_SUBSTITUTIONS.items():
                result = result.replace(formal, casual)
        elif tone_profile.formality_level == "formal":
            for casual, formal in _FORMAL_SUBSTITUTIONS.items():
                result = result.replace(casual, formal)

        return result

    def calculate_tone_score(self, response: str, profile: ToneProfile) -> float:
        if not profile.common_phrases:
            return 0.5
        text_lower = response.lower()
        matches = sum(
            1 for phrase in profile.common_phrases if phrase.lower() in text_lower
        )
        phrase_score = min(matches / max(len(profile.common_phrases), 1), 1.0)

        greeting_score = 1.0 if profile.greeting_style and profile.greeting_style.lower() in text_lower else 0.0

        return round(0.6 * phrase_score + 0.4 * greeting_score, 2)
