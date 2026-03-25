from __future__ import annotations
"""In-memory Conversation Repository — development/testing adapter."""

import asyncio

from staff_echo.domain.entities.conversation import Conversation


class InMemoryConversationRepository:

    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}
        self._lock = asyncio.Lock()

    async def save(self, conversation: Conversation) -> None:
        async with self._lock:
            self._store[conversation.id] = conversation

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        return self._store.get(conversation_id)

    async def get_by_customer_id(self, customer_id: str) -> list[Conversation]:
        return [c for c in self._store.values() if c.customer_id == customer_id]
