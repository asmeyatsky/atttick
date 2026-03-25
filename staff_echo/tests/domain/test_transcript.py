"""
Domain Tests — Transcript Aggregate

Pure unit tests for transcript lifecycle:
- Creation with segments
- Approval/rejection rules
- PII masking application
- Speaker filtering
"""

import pytest

from staff_echo.domain.entities.transcript import (
    Transcript,
    TranscriptSegment,
    TranscriptStatus,
    TranscriptError,
)
from staff_echo.domain.value_objects.speaker import Speaker, SpeakerRole
from staff_echo.domain.value_objects.pii_mask import MaskedText, PIIMask, PIIType
from staff_echo.domain.events.transcript_events import (
    TranscriptCreatedEvent,
    TranscriptApprovedEvent,
    PIIMaskedEvent,
)

_STAFF = Speaker(id="s1", name="Alice", role=SpeakerRole.STAFF)
_CUSTOMER = Speaker(id="s2", name="Bob", role=SpeakerRole.CUSTOMER)


def _make_segments() -> tuple[TranscriptSegment, ...]:
    return (
        TranscriptSegment(speaker=_CUSTOMER, text="What's the price?", start_time=0.0, end_time=2.0),
        TranscriptSegment(speaker=_STAFF, text="It's $99 per month.", start_time=2.0, end_time=4.0),
        TranscriptSegment(speaker=_STAFF, text="We also have an annual plan.", start_time=4.0, end_time=6.0),
    )


class TestTranscript:

    def test_create_sets_processed_status(self):
        transcript = Transcript.create(id="t1", audio_source="gs://bucket/audio.wav", segments=_make_segments())
        assert transcript.status == TranscriptStatus.PROCESSED
        assert len(transcript.domain_events) == 1
        assert isinstance(transcript.domain_events[0], TranscriptCreatedEvent)

    def test_staff_segments_filters_correctly(self):
        transcript = Transcript.create(id="t1", audio_source="test", segments=_make_segments())
        assert len(transcript.staff_segments) == 2
        assert all(s.speaker.role == SpeakerRole.STAFF for s in transcript.staff_segments)

    def test_customer_segments_filters_correctly(self):
        transcript = Transcript.create(id="t1", audio_source="test", segments=_make_segments())
        assert len(transcript.customer_segments) == 1
        assert transcript.customer_segments[0].speaker.role == SpeakerRole.CUSTOMER

    def test_approve_processed_transcript(self):
        transcript = Transcript.create(id="t1", audio_source="test", segments=_make_segments())
        approved = transcript.approve(approved_by="reviewer@co.com")

        assert approved.status == TranscriptStatus.APPROVED
        assert approved.approved_by == "reviewer@co.com"
        assert transcript.status == TranscriptStatus.PROCESSED  # Original unchanged
        assert any(isinstance(e, TranscriptApprovedEvent) for e in approved.domain_events)

    def test_cannot_approve_pending_transcript(self):
        transcript = Transcript(id="t1", audio_source="test", status=TranscriptStatus.PENDING)
        with pytest.raises(TranscriptError, match="PROCESSED"):
            transcript.approve("reviewer")

    def test_reject_processed_transcript(self):
        transcript = Transcript.create(id="t1", audio_source="test", segments=_make_segments())
        rejected = transcript.reject()
        assert rejected.status == TranscriptStatus.REJECTED

    def test_cannot_reject_approved_transcript(self):
        transcript = Transcript.create(id="t1", audio_source="test", segments=_make_segments())
        approved = transcript.approve("reviewer")
        with pytest.raises(TranscriptError, match="PROCESSED"):
            approved.reject()

    def test_apply_pii_masking(self):
        transcript = Transcript.create(id="t1", audio_source="test", segments=_make_segments())
        masked = MaskedText(
            original_text="Call me at 555-1234",
            masked_text="Call me at [REDACTED_PHONE]",
            masks=(PIIMask(original_span=(11, 19), pii_type=PIIType.PHONE, replacement="[REDACTED_PHONE]"),),
        )
        result = transcript.apply_pii_masking(masked)
        assert result.masked_text is not None
        assert result.masked_text.has_pii
        assert any(isinstance(e, PIIMaskedEvent) for e in result.domain_events)
