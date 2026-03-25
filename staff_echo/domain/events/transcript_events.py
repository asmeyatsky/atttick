"""
Transcript Domain Events

Architectural Intent:
- Events emitted during the transcript processing lifecycle
- TranscriptCreatedEvent: audio has been transcribed
- TranscriptApprovedEvent: staff reviewed and approved transcript for training
- PIIMaskedEvent: sensitive data was detected and redacted
"""

from dataclasses import dataclass

from staff_echo.domain.events.event_base import DomainEvent


@dataclass(frozen=True)
class TranscriptCreatedEvent(DomainEvent):
    transcript_id: str = ""
    audio_source: str = ""


@dataclass(frozen=True)
class TranscriptApprovedEvent(DomainEvent):
    transcript_id: str = ""
    approved_by: str = ""


@dataclass(frozen=True)
class PIIMaskedEvent(DomainEvent):
    transcript_id: str = ""
    masked_count: int = 0
