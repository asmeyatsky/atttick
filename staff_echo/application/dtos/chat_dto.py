from __future__ import annotations
"""
Chat DTOs

Architectural Intent:
- Pydantic models defining the contract between presentation and application layers
- Decouple domain entities from API-facing data structures
- StreamChunk supports real-time WebSocket streaming per PRD requirement
"""

from datetime import datetime

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    conversation_id: str | None = None
    customer_id: str
    message: str


class MessageDTO(BaseModel):
    id: str
    content: str
    role: str
    sources: list[str] = []
    is_verified: bool = False
    created_at: datetime


class SendMessageResponse(BaseModel):
    conversation_id: str
    response_text: str
    sources: list[str] = []
    is_verified: bool = False
    requires_handoff: bool = False


class ConversationDTO(BaseModel):
    id: str
    customer_id: str
    messages: list[MessageDTO] = []
    status: str
    created_at: datetime


class StreamChunk(BaseModel):
    conversation_id: str
    chunk: str
    is_final: bool = False
    sources: list[str] = []
    requires_handoff: bool = False
