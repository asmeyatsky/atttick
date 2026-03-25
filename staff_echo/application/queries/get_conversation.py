from __future__ import annotations
"""Get Conversation Query — reads a conversation by ID."""

from staff_echo.domain.ports.conversation_repository_port import ConversationRepositoryPort
from staff_echo.application.dtos.chat_dto import ConversationDTO, MessageDTO


class GetConversationQuery:

    def __init__(self, conversation_repo: ConversationRepositoryPort):
        self._conversation_repo = conversation_repo

    async def execute(self, conversation_id: str) -> ConversationDTO | None:
        conversation = await self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            return None
        return ConversationDTO(
            id=conversation.id,
            customer_id=conversation.customer_id,
            messages=[
                MessageDTO(
                    id=m.id,
                    content=m.content.text,
                    role=m.content.role.value,
                    sources=list(m.sources),
                    is_verified=m.is_verified,
                    created_at=m.created_at,
                )
                for m in conversation.messages
            ],
            status=conversation.status.value,
            created_at=conversation.created_at,
        )
