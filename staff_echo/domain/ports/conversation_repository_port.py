from __future__ import annotations
"""Conversation Repository Port — defines the contract for conversation persistence."""

from typing import Protocol

from staff_echo.domain.entities.conversation import Conversation


class ConversationRepositoryPort(Protocol):
    async def save(self, conversation: Conversation) -> None: ...
    async def get_by_id(self, conversation_id: str) -> Conversation | None: ...
    async def get_by_customer_id(self, customer_id: str) -> list[Conversation]: ...
