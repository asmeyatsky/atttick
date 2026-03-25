"""
Application Tests — SendMessage Use Case

Tests with mocked ports, verifying orchestration logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from staff_echo.application.commands.send_message import SendMessageUseCase
from staff_echo.application.dtos.chat_dto import SendMessageRequest
from staff_echo.domain.entities.conversation import Conversation
from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource
from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.services.pricing_validation_service import PricingValidationService


@pytest.fixture
def mocked_use_case():
    conversation_repo = AsyncMock()
    conversation_repo.get_by_id = AsyncMock(return_value=None)

    knowledge_repo = AsyncMock()
    knowledge_repo.search = AsyncMock(return_value=[
        KnowledgeEntry(id="k1", category=KnowledgeCategory.FAQ, content="Our hours are 9-5"),
    ])
    knowledge_repo.get_pricing = AsyncMock(return_value=[])

    ai_provider = AsyncMock()
    ai_provider.generate_response_full = AsyncMock(
        return_value="Thanks for asking! Our hours are 9-5 weekdays."
    )

    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()

    event_bus = AsyncMock()
    event_bus.publish = AsyncMock()

    return SendMessageUseCase(
        conversation_repo=conversation_repo,
        knowledge_repo=knowledge_repo,
        ai_provider=ai_provider,
        cache=cache,
        event_bus=event_bus,
        tone_service=ToneAlignmentService(),
        pricing_service=PricingValidationService(),
    ), conversation_repo, event_bus


@pytest.mark.asyncio
async def test_send_message_creates_conversation(mocked_use_case):
    use_case, conv_repo, event_bus = mocked_use_case
    request = SendMessageRequest(customer_id="cust-1", message="What are your hours?")

    result = await use_case.execute(request)

    assert result.conversation_id
    assert result.response_text
    assert not result.requires_handoff
    conv_repo.save.assert_awaited_once()
    event_bus.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_with_existing_conversation(mocked_use_case):
    use_case, conv_repo, _ = mocked_use_case
    existing = Conversation(id="existing-conv", customer_id="cust-1")
    conv_repo.get_by_id = AsyncMock(return_value=existing)

    request = SendMessageRequest(
        conversation_id="existing-conv",
        customer_id="cust-1",
        message="Follow up question",
    )

    result = await use_case.execute(request)
    assert result.conversation_id == "existing-conv"


@pytest.mark.asyncio
async def test_send_message_triggers_handoff_for_bad_pricing():
    conversation_repo = AsyncMock()
    conversation_repo.get_by_id = AsyncMock(return_value=None)

    knowledge_repo = AsyncMock()
    knowledge_repo.search = AsyncMock(return_value=[])
    knowledge_repo.get_pricing = AsyncMock(return_value=[
        PricingInfo(amount=99.0, currency="USD", product_id="basic", source=PricingSource.BIGQUERY_VERIFIED),
    ])

    ai_provider = AsyncMock()
    ai_provider.generate_response_full = AsyncMock(
        return_value="I can offer that for $50.00!"
    )

    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)

    event_bus = AsyncMock()
    event_bus.publish = AsyncMock()

    use_case = SendMessageUseCase(
        conversation_repo=conversation_repo,
        knowledge_repo=knowledge_repo,
        ai_provider=ai_provider,
        cache=cache,
        event_bus=event_bus,
        tone_service=ToneAlignmentService(),
        pricing_service=PricingValidationService(),
    )

    request = SendMessageRequest(customer_id="cust-1", message="How much is the basic plan?")
    result = await use_case.execute(request)

    assert result.requires_handoff
