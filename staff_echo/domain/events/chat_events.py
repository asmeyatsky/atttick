"""
Chat Domain Events

Architectural Intent:
- Events emitted by the Conversation aggregate during chat lifecycle
- MessageReceivedEvent: customer sent a message
- ResponseGeneratedEvent: AI response produced with optional source citations
- HandoffTriggeredEvent: conversation escalated to human agent
"""

from dataclasses import dataclass

from staff_echo.domain.events.event_base import DomainEvent


@dataclass(frozen=True)
class MessageReceivedEvent(DomainEvent):
    conversation_id: str = ""
    content: str = ""


@dataclass(frozen=True)
class ResponseGeneratedEvent(DomainEvent):
    conversation_id: str = ""
    content: str = ""
    sources_cited: tuple[str, ...] = ()


@dataclass(frozen=True)
class HandoffTriggeredEvent(DomainEvent):
    conversation_id: str = ""
    reason: str = ""
