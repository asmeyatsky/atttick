"""
Send Message Streaming Use Case

Architectural Intent:
- Streaming variant of SendMessage for WebSocket real-time responses
- Yields StreamChunk objects as the AI generates text
- Final chunk includes sources, verification status, and handoff info
- Uses the same knowledge retrieval and pricing validation pipeline
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator

from staff_echo.domain.entities.conversation import Conversation
from staff_echo.domain.entities.message import Message
from staff_echo.domain.value_objects.message_content import MessageContent, MessageRole
from staff_echo.domain.ports.conversation_repository_port import ConversationRepositoryPort
from staff_echo.domain.ports.knowledge_repository_port import KnowledgeRepositoryPort
from staff_echo.domain.ports.ai_provider_port import AIProviderPort
from staff_echo.domain.ports.cache_port import CachePort
from staff_echo.domain.ports.event_bus_port import EventBusPort
from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.services.pricing_validation_service import PricingValidationService
from staff_echo.application.dtos.chat_dto import SendMessageRequest, StreamChunk


class SendMessageStreamingUseCase:

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
        self._ai_provider = ai_provider
        self._cache = cache
        self._event_bus = event_bus
        self._tone_service = tone_service
        self._pricing_service = pricing_service

    async def execute(
        self, request: SendMessageRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        # Get or create conversation
        conversation = await self._get_or_create_conversation(request)

        # Add user message
        user_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            content=MessageContent(text=request.message, role=MessageRole.USER),
        )
        conversation = conversation.add_message(user_message)

        # Parallel: knowledge + pricing
        knowledge_entries, pricing_data = await asyncio.gather(
            self._knowledge_repo.search(request.message, limit=5),
            self._get_pricing(request.message),
        )

        # Build context
        context_parts = []
        for entry in knowledge_entries:
            context_parts.append(f"[{entry.category.value}] {entry.content}")
        context = "\n".join(context_parts) if context_parts else "No specific knowledge found."
        sources = tuple(e.id for e in knowledge_entries)

        # Stream AI response
        message_history = [msg.content for msg in conversation.messages]
        full_response = ""

        async for chunk in self._ai_provider.generate_response(
            messages=message_history,
            context=context,
            tone_profile=conversation.tone_profile,
        ):
            full_response += chunk
            yield StreamChunk(
                conversation_id=conversation.id,
                chunk=chunk,
                is_final=False,
            )

        # Validate pricing in complete response
        validation = self._pricing_service.validate_pricing_response(
            full_response, pricing_data
        )
        requires_handoff = validation.requires_handoff
        is_verified = any(
            e.has_verified_pricing for e in knowledge_entries if e.is_pricing
        )

        if requires_handoff:
            conversation = conversation.handoff_to_human(validation.reason)

        # Add assistant message and persist
        assistant_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            content=MessageContent(text=full_response, role=MessageRole.ASSISTANT),
            sources=sources,
            is_verified=is_verified,
        )
        if not requires_handoff:
            conversation = conversation.add_message(assistant_message)
        await self._conversation_repo.save(conversation)
        await self._event_bus.publish(list(conversation.domain_events))

        # Final chunk with metadata
        yield StreamChunk(
            conversation_id=conversation.id,
            chunk="",
            is_final=True,
            sources=list(sources),
            requires_handoff=requires_handoff,
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

    async def _get_pricing(self, query: str):
        from staff_echo.domain.value_objects.pricing_info import PricingInfo

        all_pricing: list[PricingInfo] = []
        for word in query.lower().split():
            if len(word) > 3:
                all_pricing.extend(await self._knowledge_repo.get_pricing(word))
        return all_pricing
