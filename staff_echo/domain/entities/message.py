"""
Message Entity

Architectural Intent:
- Represents a single message within a conversation
- Immutable — source citations and verification produce new instances
- Sources track which knowledge entries informed the response
- Verification marks pricing data as staff-history-confirmed
"""

from dataclasses import dataclass, replace, field
from datetime import datetime, UTC

from staff_echo.domain.value_objects.message_content import MessageContent


@dataclass(frozen=True)
class Message:
    id: str
    conversation_id: str
    content: MessageContent
    sources: tuple[str, ...] = ()
    is_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_source_citation(self, source: str) -> "Message":
        return replace(self, sources=self.sources + (source,))

    def mark_as_verified(self) -> "Message":
        return replace(self, is_verified=True)
