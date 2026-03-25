"""
Handoff to Human Use Case

Architectural Intent:
- Escalates a conversation to a human agent
- Triggered when pricing validation fails or AI cannot answer confidently
- Enforces PRD requirement: never hallucinate prices, hand off instead
"""

from staff_echo.domain.ports.conversation_repository_port import ConversationRepositoryPort
from staff_echo.domain.ports.event_bus_port import EventBusPort
from staff_echo.application.dtos.chat_dto import ConversationDTO, MessageDTO


class HandoffToHumanUseCase:

    def __init__(
        self,
        conversation_repo: ConversationRepositoryPort,
        event_bus: EventBusPort,
    ):
        self._conversation_repo = conversation_repo
        self._event_bus = event_bus

    async def execute(self, conversation_id: str, reason: str) -> ConversationDTO:
        conversation = await self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation = conversation.handoff_to_human(reason)

        await self._conversation_repo.save(conversation)
        await self._event_bus.publish(list(conversation.domain_events))

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
