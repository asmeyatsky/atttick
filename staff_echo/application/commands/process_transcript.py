"""
Process Transcript Use Case

Architectural Intent:
- Orchestrates the audio-to-transcript pipeline
- Steps: transcribe -> diarize -> detect PII -> mask PII -> persist
- Implements the PRD's data processing pipeline requirements
"""

import uuid

from staff_echo.domain.entities.transcript import Transcript
from staff_echo.domain.ports.transcript_repository_port import TranscriptRepositoryPort
from staff_echo.domain.ports.transcription_port import TranscriptionPort
from staff_echo.domain.ports.pii_detector_port import PIIDetectorPort
from staff_echo.domain.ports.event_bus_port import EventBusPort
from staff_echo.domain.services.pii_masking_service import PIIMaskingService
from staff_echo.application.dtos.transcript_dto import (
    ProcessTranscriptRequest,
    TranscriptDTO,
    SegmentDTO,
)


class ProcessTranscriptUseCase:

    def __init__(
        self,
        transcript_repo: TranscriptRepositoryPort,
        transcription: TranscriptionPort,
        pii_detector: PIIDetectorPort,
        pii_service: PIIMaskingService,
        event_bus: EventBusPort,
    ):
        self._transcript_repo = transcript_repo
        self._transcription = transcription
        self._pii_detector = pii_detector
        self._pii_service = pii_service
        self._event_bus = event_bus

    async def execute(self, request: ProcessTranscriptRequest) -> TranscriptDTO:
        # Step 1: Transcribe audio with speaker diarization
        segments = await self._transcription.transcribe(request.audio_source)

        # Step 2: Create transcript aggregate
        transcript = Transcript.create(
            id=str(uuid.uuid4()),
            audio_source=request.audio_source,
            segments=tuple(segments),
        )

        # Step 3: Detect and mask PII in all segments
        full_text = " ".join(s.text for s in segments)
        detections = self._pii_detector.detect(full_text)
        if detections:
            masked = self._pii_service.mask_text(full_text, detections)
            transcript = transcript.apply_pii_masking(masked)

        # Step 4: Persist
        await self._transcript_repo.save(transcript)

        # Step 5: Publish events
        await self._event_bus.publish(list(transcript.domain_events))

        return self._to_dto(transcript)

    def _to_dto(self, transcript: Transcript) -> TranscriptDTO:
        return TranscriptDTO(
            id=transcript.id,
            audio_source=transcript.audio_source,
            segments=[
                SegmentDTO(
                    speaker_name=s.speaker.name,
                    speaker_role=s.speaker.role.value,
                    text=s.text,
                    start_time=s.start_time,
                    end_time=s.end_time,
                )
                for s in transcript.segments
            ],
            status=transcript.status.value,
            created_at=transcript.created_at,
        )
