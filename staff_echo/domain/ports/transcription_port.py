"""Transcription Port — defines the contract for speech-to-text services."""

from typing import Protocol

from staff_echo.domain.entities.transcript import TranscriptSegment


class TranscriptionPort(Protocol):
    async def transcribe(self, audio_source: str) -> list[TranscriptSegment]: ...

    @property
    def supports_diarization(self) -> bool: ...
