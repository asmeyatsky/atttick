"""
Transcript DTOs

Architectural Intent:
- Data transfer objects for the transcript processing pipeline
- Maps domain Transcript aggregate to API-facing structures
"""

from datetime import datetime

from pydantic import BaseModel


class ProcessTranscriptRequest(BaseModel):
    audio_source: str


class SegmentDTO(BaseModel):
    speaker_name: str
    speaker_role: str
    text: str
    start_time: float
    end_time: float


class TranscriptDTO(BaseModel):
    id: str
    audio_source: str
    segments: list[SegmentDTO] = []
    status: str
    created_at: datetime


class ApproveTranscriptRequest(BaseModel):
    transcript_id: str
    approved_by: str
