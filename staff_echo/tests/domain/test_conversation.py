"""
Domain Tests — Conversation Aggregate

Pure unit tests, no mocks needed. Tests domain invariants:
- Immutability (state changes produce new instances)
- Status transition rules
- Domain event collection
"""

import pytest
from datetime import datetime, UTC

from staff_echo.domain.entities.conversation import (
    Conversation,
    ConversationStatus,
    ConversationError,
)
from staff_echo.domain.entities.message import Message
from staff_echo.domain.value_objects.message_content import MessageContent, MessageRole
from staff_echo.domain.events.chat_events import MessageReceivedEvent, HandoffTriggeredEvent


def _make_message(conversation_id: str = "conv-1", text: str = "Hello") -> Message:
    return Message(
        id="msg-1",
        conversation_id=conversation_id,
        content=MessageContent(text=text, role=MessageRole.USER),
    )


class TestConversation:

    def test_new_conversation_is_active(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        assert conv.status == ConversationStatus.ACTIVE
        assert conv.message_count == 0
        assert conv.last_message is None

    def test_add_message_creates_new_instance(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        msg = _make_message("conv-1")
        new_conv = conv.add_message(msg)

        assert new_conv is not conv
        assert new_conv.message_count == 1
        assert conv.message_count == 0  # Original unchanged
        assert new_conv.last_message is msg

    def test_add_message_emits_event(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        msg = _make_message("conv-1", "Test message")
        new_conv = conv.add_message(msg)

        assert len(new_conv.domain_events) == 1
        event = new_conv.domain_events[0]
        assert isinstance(event, MessageReceivedEvent)
        assert event.conversation_id == "conv-1"
        assert event.content == "Test message"

    def test_cannot_add_message_to_handed_off_conversation(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        handed_off = conv.handoff_to_human("pricing issue")
        msg = _make_message("conv-1")

        with pytest.raises(ConversationError, match="handed_off"):
            handed_off.add_message(msg)

    def test_cannot_add_message_to_closed_conversation(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        closed = conv.close()
        msg = _make_message("conv-1")

        with pytest.raises(ConversationError, match="closed"):
            closed.add_message(msg)

    def test_handoff_to_human(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        handed_off = conv.handoff_to_human("unknown pricing")

        assert handed_off.status == ConversationStatus.HANDED_OFF
        assert conv.status == ConversationStatus.ACTIVE  # Original unchanged
        assert len(handed_off.domain_events) == 1
        event = handed_off.domain_events[0]
        assert isinstance(event, HandoffTriggeredEvent)
        assert event.reason == "unknown pricing"

    def test_close_conversation(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        closed = conv.close()
        assert closed.status == ConversationStatus.CLOSED

    def test_multiple_messages_accumulate_events(self):
        conv = Conversation(id="conv-1", customer_id="cust-1")
        msg1 = Message(id="m1", conversation_id="conv-1", content=MessageContent(text="Hi", role=MessageRole.USER))
        msg2 = Message(id="m2", conversation_id="conv-1", content=MessageContent(text="Hello", role=MessageRole.ASSISTANT))

        conv = conv.add_message(msg1)
        conv = conv.add_message(msg2)

        assert conv.message_count == 2
        assert len(conv.domain_events) == 2
