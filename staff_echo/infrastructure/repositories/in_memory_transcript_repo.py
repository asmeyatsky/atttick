from __future__ import annotations
"""In-memory Transcript Repository — development/testing adapter."""

import asyncio

from staff_echo.domain.entities.transcript import Transcript, TranscriptStatus


class InMemoryTranscriptRepository:

    def __init__(self) -> None:
        self._store: dict[str, Transcript] = {}
        self._lock = asyncio.Lock()

    async def save(self, transcript: Transcript) -> None:
        async with self._lock:
            self._store[transcript.id] = transcript

    async def get_by_id(self, transcript_id: str) -> Transcript | None:
        return self._store.get(transcript_id)

    async def get_pending(self) -> list[Transcript]:
        return [
            t for t in self._store.values()
            if t.status == TranscriptStatus.PENDING
        ]

    async def get_approved(self) -> list[Transcript]:
        return [
            t for t in self._store.values()
            if t.status == TranscriptStatus.APPROVED
        ]
