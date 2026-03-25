"""
Application Tests — ProcessTranscript Use Case

Tests the transcript processing pipeline with mocked ports.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from staff_echo.application.commands.process_transcript import ProcessTranscriptUseCase
from staff_echo.application.dtos.transcript_dto import ProcessTranscriptRequest
from staff_echo.domain.entities.transcript import TranscriptSegment
from staff_echo.domain.value_objects.speaker import Speaker, SpeakerRole
from staff_echo.domain.value_objects.pii_mask import PIIMask, PIIType
from staff_echo.domain.services.pii_masking_service import PIIMaskingService


@pytest.fixture
def mocked_use_case():
    staff = Speaker(id="s1", name="Staff", role=SpeakerRole.STAFF)
    customer = Speaker(id="s2", name="Customer", role=SpeakerRole.CUSTOMER)

    transcript_repo = AsyncMock()
    transcription = AsyncMock()
    transcription.transcribe = AsyncMock(return_value=[
        TranscriptSegment(speaker=customer, text="My email is test@test.com", start_time=0.0, end_time=2.0),
        TranscriptSegment(speaker=staff, text="Got it, let me help you.", start_time=2.0, end_time=4.0),
    ])

    pii_detector = MagicMock()
    pii_detector.detect = MagicMock(return_value=[
        PIIMask(original_span=(12, 25), pii_type=PIIType.EMAIL, replacement="[REDACTED_EMAIL]"),
    ])

    event_bus = AsyncMock()
    event_bus.publish = AsyncMock()

    return ProcessTranscriptUseCase(
        transcript_repo=transcript_repo,
        transcription=transcription,
        pii_detector=pii_detector,
        pii_service=PIIMaskingService(),
        event_bus=event_bus,
    ), transcript_repo, event_bus


@pytest.mark.asyncio
async def test_process_transcript(mocked_use_case):
    use_case, transcript_repo, event_bus = mocked_use_case
    request = ProcessTranscriptRequest(audio_source="gs://bucket/call.wav")

    result = await use_case.execute(request)

    assert result.status == "processed"
    assert len(result.segments) == 2
    transcript_repo.save.assert_awaited_once()
    event_bus.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_transcript_detects_pii(mocked_use_case):
    use_case, transcript_repo, _ = mocked_use_case
    request = ProcessTranscriptRequest(audio_source="gs://bucket/call.wav")

    await use_case.execute(request)

    saved_transcript = transcript_repo.save.call_args[0][0]
    assert saved_transcript.masked_text is not None
    assert saved_transcript.masked_text.has_pii
