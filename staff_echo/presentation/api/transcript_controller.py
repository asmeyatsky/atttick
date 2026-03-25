from __future__ import annotations
"""
Transcript Controller — REST endpoints for the transcript processing pipeline.

Architectural Intent:
- Exposes transcript processing, approval, and status endpoints
- Delegates to application use cases
"""

from fastapi import APIRouter, Request, HTTPException

from staff_echo.application.dtos.transcript_dto import (
    ProcessTranscriptRequest,
    ApproveTranscriptRequest,
    TranscriptDTO,
)

transcript_router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])


@transcript_router.post("/process", response_model=TranscriptDTO)
async def process_transcript(request: ProcessTranscriptRequest, req: Request):
    container = req.app.state.container
    use_case = container.process_transcript_use_case
    return await use_case.execute(request)


@transcript_router.post("/approve", response_model=TranscriptDTO)
async def approve_transcript(request: ApproveTranscriptRequest, req: Request):
    container = req.app.state.container
    use_case = container.approve_transcript_use_case
    try:
        return await use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@transcript_router.get("/{transcript_id}", response_model=TranscriptDTO | None)
async def get_transcript(transcript_id: str, req: Request):
    container = req.app.state.container
    query = container.get_transcript_status_query
    result = await query.execute(transcript_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return result
