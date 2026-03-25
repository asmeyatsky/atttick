"""
Send Message Use Case

Architectural Intent:
- Primary command for processing customer chat messages
- Orchestrates: conversation management, knowledge retrieval, AI response, pricing validation
- Uses ChatResponseWorkflow for the response generation pipeline
- Publishes domain events after successful persistence
"""

import uuid
from datetime import datetime, UTC

from staff_echo.domain.entities.conversation import Conversation, ConversationStatus
from staff_echo.domain.entities.message import Message
from staff_echo.domain.value_objects.message_content import MessageContent, MessageRole
from staff_echo.domain.ports.conversation_repository_port import ConversationRepositoryPort
from staff_echo.domain.ports.knowledge_repository_port import KnowledgeRepositoryPort
from staff_echo.domain.ports.ai_provider_port import AIProviderPort
from staff_echo.domain.ports.cache_port import CachePort
from staff_echo.domain.ports.event_bus_port import EventBusPort
from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.services.pricing_validation_service import PricingValidationService
from staff_echo.application.dtos.chat_dto import SendMessageRequest, SendMessageResponse
from staff_echo.application.orchestration.chat_response_workflow import ChatResponseWorkflow


class SendMessageUseCase:

    def __init__(
        self,
        conversation_repo: ConversationRepositoryPort,
        knowledge_repo: KnowledgeRepositoryPort,
        ai_provider: AIProviderPort,
        cache: CachePort,
        event_bus: EventBusPort,
        tone_service: ToneAlignmentService,
        pricing_service: PricingValidationService,
    ):
        self._conversation_repo = conversation_repo
        self._knowledge_repo = knowledge_repo
        self._event_bus = event_bus
        self._workflow = ChatResponseWorkflow(
            knowledge_repo=knowledge_repo,
            ai_provider=ai_provider,
            cache=cache,
            tone_service=tone_service,
            pricing_service=pricing_service,
        )

    async def execute(self, request: SendMessageRequest) -> SendMessageResponse:
        # Step 1: Get or create conversation
        conversation = await self._get_or_create_conversation(request)

        # Step 2: Add user message
        user_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            content=MessageContent(text=request.message, role=MessageRole.USER),
        )
        conversation = conversation.add_message(user_message)

        # Step 3: Build message history for AI context
        message_history = [msg.content for msg in conversation.messages]

        # Step 4: Execute response workflow (parallel knowledge + pricing + AI)
        result = await self._workflow.execute(
            messages=message_history,
            user_query=request.message,
            tone_profile=conversation.tone_profile,
        )

        # Step 5: Handle handoff if needed
        if result.requires_handoff:
            conversation = conversation.handoff_to_human(result.handoff_reason)
            await self._conversation_repo.save(conversation)
            await self._event_bus.publish(list(conversation.domain_events))
            return SendMessageResponse(
                conversation_id=conversation.id,
                response_text="I want to make sure you get the most accurate information. "
                "Let me connect you with a team member who can help with this. "
                f"Reason: {result.handoff_reason}",
                sources=list(result.sources),
                is_verified=False,
                requires_handoff=True,
            )

        # Step 6: Add assistant message
        assistant_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            content=MessageContent(text=result.response_text, role=MessageRole.ASSISTANT),
            sources=result.sources,
            is_verified=result.is_verified,
        )
        conversation = conversation.add_message(assistant_message)

        # Step 7: Persist and publish events
        await self._conversation_repo.save(conversation)
        await self._event_bus.publish(list(conversation.domain_events))

        return SendMessageResponse(
            conversation_id=conversation.id,
            response_text=result.response_text,
            sources=list(result.sources),
            is_verified=result.is_verified,
            requires_handoff=False,
        )

    async def _get_or_create_conversation(
        self, request: SendMessageRequest
    ) -> Conversation:
        if request.conversation_id:
            existing = await self._conversation_repo.get_by_id(request.conversation_id)
            if existing:
                return existing
        return Conversation(
            id=request.conversation_id or str(uuid.uuid4()),
            customer_id=request.customer_id,
        )
