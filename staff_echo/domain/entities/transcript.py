from __future__ import annotations
"""
Transcript Aggregate

Architectural Intent:
- Manages the lifecycle of audio transcription from staff recordings
- TranscriptSegment captures diarized speech with speaker attribution
- Enforces review-and-approve workflow before training data is used
- PII masking applied before any data enters the AI pipeline

Key Design Decisions:
1. Only PROCESSED transcripts can be approved/rejected (review gate)
2. Staff segments filtered for tone extraction, customer segments excluded
3. PII masking is a domain concern tracked with events
"""

from dataclasses import dataclass, replace, field
from datetime import datetime, UTC
from enum import Enum

from staff_echo.domain.events.event_base import DomainEvent
from staff_echo.domain.events.transcript_events import (
    TranscriptCreatedEvent,
    TranscriptApprovedEvent,
    PIIMaskedEvent,
)
from staff_echo.domain.value_objects.speaker import Speaker, SpeakerRole
from staff_echo.domain.value_objects.pii_mask import MaskedText


class TranscriptStatus(Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TranscriptError(Exception):
    pass


@dataclass(frozen=True)
class TranscriptSegment:
    speaker: Speaker
    text: str
    start_time: float
    end_time: float


@dataclass(frozen=True)
class Transcript:
    id: str
    audio_source: str
    segments: tuple[TranscriptSegment, ...] = ()
    status: TranscriptStatus = TranscriptStatus.PENDING
    masked_text: MaskedText | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    approved_by: str | None = None
    domain_events: tuple[DomainEvent, ...] = ()

    @staticmethod
    def create(
        id: str, audio_source: str, segments: tuple[TranscriptSegment, ...]
    ) -> "Transcript":
        event = TranscriptCreatedEvent(
            aggregate_id=id,
            transcript_id=id,
            audio_source=audio_source,
        )
        return Transcript(
            id=id,
            audio_source=audio_source,
            segments=segments,
            status=TranscriptStatus.PROCESSED,
            domain_events=(event,),
        )

    @property
    def staff_segments(self) -> tuple[TranscriptSegment, ...]:
        return tuple(
            s for s in self.segments if s.speaker.role == SpeakerRole.STAFF
        )

    @property
    def customer_segments(self) -> tuple[TranscriptSegment, ...]:
        return tuple(
            s for s in self.segments if s.speaker.role == SpeakerRole.CUSTOMER
        )

    def approve(self, approved_by: str) -> "Transcript":
        if self.status != TranscriptStatus.PROCESSED:
            raise TranscriptError(
                f"Only PROCESSED transcripts can be approved, current: {self.status.value}"
            )
        event = TranscriptApprovedEvent(
            aggregate_id=self.id,
            transcript_id=self.id,
            approved_by=approved_by,
        )
        return replace(
            self,
            status=TranscriptStatus.APPROVED,
            approved_by=approved_by,
            domain_events=self.domain_events + (event,),
        )

    def reject(self) -> "Transcript":
        if self.status != TranscriptStatus.PROCESSED:
            raise TranscriptError(
                f"Only PROCESSED transcripts can be rejected, current: {self.status.value}"
            )
        return replace(self, status=TranscriptStatus.REJECTED)

    def apply_pii_masking(self, masked_text: MaskedText) -> "Transcript":
        event = PIIMaskedEvent(
            aggregate_id=self.id,
            transcript_id=self.id,
            masked_count=masked_text.mask_count,
        )
        return replace(
            self,
            masked_text=masked_text,
            domain_events=self.domain_events + (event,),
        )
