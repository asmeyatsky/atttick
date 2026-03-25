"""
Domain Tests — Tone Alignment Service

Tests tone alignment and scoring logic.
"""

from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.value_objects.tone_profile import ToneProfile


class TestToneAlignmentService:

    def setup_method(self):
        self.service = ToneAlignmentService()
        self.profile = ToneProfile(
            greeting_style="Hey there!",
            formality_level="casual",
            common_phrases=("happy to help", "no worries"),
            analogies=("think of it like",),
        )

    def test_align_adds_greeting(self):
        response = "I can help you with that."
        result = self.service.align_response(response, self.profile)
        assert result.startswith("Hey there!")

    def test_align_casual_substitutions(self):
        response = "I would like to inform you that your order is ready."
        result = self.service.align_response(response, self.profile)
        assert "Just letting you know" in result

    def test_score_with_matching_phrases(self):
        response = "Hey there! I'm happy to help you out, no worries at all."
        score = self.service.calculate_tone_score(response, self.profile)
        assert score > 0.5

    def test_score_with_no_matching_phrases(self):
        response = "The product specifications are as follows."
        score = self.service.calculate_tone_score(response, self.profile)
        assert score < 0.5

    def test_score_with_empty_phrases(self):
        empty_profile = ToneProfile(
            greeting_style="Hi",
            formality_level="professional",
            common_phrases=(),
        )
        score = self.service.calculate_tone_score("Any response", empty_profile)
        assert score == 0.5  # Default when no phrases to match
