from __future__ import annotations
"""Get Transcript Status Query — reads transcript status by ID."""

from staff_echo.domain.ports.transcript_repository_port import TranscriptRepositoryPort
from staff_echo.application.dtos.transcript_dto import TranscriptDTO, SegmentDTO


class GetTranscriptStatusQuery:

    def __init__(self, transcript_repo: TranscriptRepositoryPort):
        self._transcript_repo = transcript_repo

    async def execute(self, transcript_id: str) -> TranscriptDTO | None:
        transcript = await self._transcript_repo.get_by_id(transcript_id)
        if not transcript:
            return None
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
