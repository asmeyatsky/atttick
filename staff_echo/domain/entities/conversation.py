from __future__ import annotations
"""
Conversation Aggregate

Architectural Intent:
- The primary aggregate for the Chat bounded context
- Manages the lifecycle of a customer chat session
- Enforces invariants: no messages after handoff/close
- Collects domain events for cross-context communication
- ToneProfile attached per conversation to maintain consistent staff voice

Key Design Decisions:
1. Conversations are immutable — state changes produce new instances
2. Status transitions enforce valid lifecycle (ACTIVE -> HANDED_OFF/CLOSED)
3. Domain events collected, not fired inline — dispatched after persistence
"""

from dataclasses import dataclass, replace, field
from datetime import datetime, UTC
from enum import Enum

from staff_echo.domain.entities.message import Message
from staff_echo.domain.events.event_base import DomainEvent
from staff_echo.domain.events.chat_events import (
    MessageReceivedEvent,
    HandoffTriggeredEvent,
)
from staff_echo.domain.value_objects.tone_profile import ToneProfile


class ConversationStatus(Enum):
    ACTIVE = "active"
    HANDED_OFF = "handed_off"
    CLOSED = "closed"


class ConversationError(Exception):
    pass


@dataclass(frozen=True)
class Conversation:
    id: str
    customer_id: str
    messages: tuple[Message, ...] = ()
    status: ConversationStatus = ConversationStatus.ACTIVE
    tone_profile: ToneProfile | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    domain_events: tuple[DomainEvent, ...] = ()

    def add_message(self, message: Message) -> "Conversation":
        if self.status != ConversationStatus.ACTIVE:
            raise ConversationError(
                f"Cannot add messages to {self.status.value} conversation"
            )
        event = MessageReceivedEvent(
            aggregate_id=self.id,
            conversation_id=self.id,
            content=message.content.text,
        )
        return replace(
            self,
            messages=self.messages + (message,),
            domain_events=self.domain_events + (event,),
        )

    def handoff_to_human(self, reason: str) -> "Conversation":
        if self.status != ConversationStatus.ACTIVE:
            raise ConversationError(
                f"Cannot hand off {self.status.value} conversation"
            )
        event = HandoffTriggeredEvent(
            aggregate_id=self.id,
            conversation_id=self.id,
            reason=reason,
        )
        return replace(
            self,
            status=ConversationStatus.HANDED_OFF,
            domain_events=self.domain_events + (event,),
        )

    def close(self) -> "Conversation":
        return replace(self, status=ConversationStatus.CLOSED)

    @property
    def last_message(self) -> Message | None:
        return self.messages[-1] if self.messages else None

    @property
    def message_count(self) -> int:
        return len(self.messages)
