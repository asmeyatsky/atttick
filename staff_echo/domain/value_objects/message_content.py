"""
Message Content Value Object

Architectural Intent:
- Immutable representation of a chat message's content and metadata
- MessageRole maps to the chat protocol (user/assistant/system)
- Timestamp captures when the content was created
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class MessageContent:
    text: str
    role: MessageRole
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()
