"""
Approve Transcript Use Case

Architectural Intent:
- Implements the PRD's "Review & Approve" layer for transcriptions
- Only approved transcripts are used for training data
- Extracts knowledge entries from staff segments upon approval
- Guards against noisy/off-script data entering the AI pipeline
"""

import uuid

from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.entities.transcript import TranscriptError
from staff_echo.domain.ports.transcript_repository_port import TranscriptRepositoryPort
from staff_echo.domain.ports.knowledge_repository_port import KnowledgeRepositoryPort
from staff_echo.domain.ports.event_bus_port import EventBusPort
from staff_echo.application.dtos.transcript_dto import (
    ApproveTranscriptRequest,
    TranscriptDTO,
    SegmentDTO,
)


class ApproveTranscriptUseCase:

    def __init__(
        self,
        transcript_repo: TranscriptRepositoryPort,
        knowledge_repo: KnowledgeRepositoryPort,
        event_bus: EventBusPort,
    ):
        self._transcript_repo = transcript_repo
        self._knowledge_repo = knowledge_repo
        self._event_bus = event_bus

    async def execute(self, request: ApproveTranscriptRequest) -> TranscriptDTO:
        transcript = await self._transcript_repo.get_by_id(request.transcript_id)
        if not transcript:
            raise ValueError(f"Transcript {request.transcript_id} not found")

        # Approve the transcript
        transcript = transcript.approve(approved_by=request.approved_by)

        # Extract knowledge from staff segments
        for segment in transcript.staff_segments:
            entry = KnowledgeEntry(
                id=str(uuid.uuid4()),
                category=KnowledgeCategory.GENERAL,
                content=segment.text,
                source_transcript_id=transcript.id,
            )
            await self._knowledge_repo.save(entry)

        # Persist and publish
        await self._transcript_repo.save(transcript)
        await self._event_bus.publish(list(transcript.domain_events))

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
