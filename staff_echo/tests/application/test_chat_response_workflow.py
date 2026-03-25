"""
Application Tests — Chat Response Workflow

Tests the DAG orchestration: parallel knowledge/pricing lookup, AI generation, validation.
"""

import pytest
from unittest.mock import AsyncMock

from staff_echo.application.orchestration.chat_response_workflow import ChatResponseWorkflow
from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.message_content import MessageContent, MessageRole
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource
from staff_echo.domain.value_objects.tone_profile import ToneProfile
from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.services.pricing_validation_service import PricingValidationService


@pytest.fixture
def workflow():
    knowledge_repo = AsyncMock()
    knowledge_repo.search = AsyncMock(return_value=[
        KnowledgeEntry(id="k1", category=KnowledgeCategory.FAQ, content="Open 9-5"),
    ])
    knowledge_repo.get_pricing = AsyncMock(return_value=[])

    ai_provider = AsyncMock()
    ai_provider.generate_response_full = AsyncMock(return_value="We're open 9-5 weekdays.")

    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()

    return ChatResponseWorkflow(
        knowledge_repo=knowledge_repo,
        ai_provider=ai_provider,
        cache=cache,
        tone_service=ToneAlignmentService(),
        pricing_service=PricingValidationService(),
    )


@pytest.mark.asyncio
async def test_workflow_returns_response(workflow):
    messages = [MessageContent(text="What are your hours?", role=MessageRole.USER)]
    result = await workflow.execute(messages, "What are your hours?")

    assert result.response_text
    assert not result.requires_handoff
    assert len(result.sources) > 0


@pytest.mark.asyncio
async def test_workflow_returns_cached_response():
    knowledge_repo = AsyncMock()
    ai_provider = AsyncMock()
    cache = AsyncMock()
    cache.get = AsyncMock(return_value="Cached answer!")

    wf = ChatResponseWorkflow(
        knowledge_repo=knowledge_repo,
        ai_provider=ai_provider,
        cache=cache,
        tone_service=ToneAlignmentService(),
        pricing_service=PricingValidationService(),
    )

    messages = [MessageContent(text="FAQ question", role=MessageRole.USER)]
    result = await wf.execute(messages, "FAQ question")

    assert result.response_text == "Cached answer!"
    ai_provider.generate_response_full.assert_not_awaited()


@pytest.mark.asyncio
async def test_workflow_triggers_handoff_for_invalid_pricing():
    knowledge_repo = AsyncMock()
    knowledge_repo.search = AsyncMock(return_value=[])
    knowledge_repo.get_pricing = AsyncMock(return_value=[
        PricingInfo(amount=100.0, currency="USD", product_id="plan", source=PricingSource.BIGQUERY_VERIFIED),
    ])

    ai_provider = AsyncMock()
    ai_provider.generate_response_full = AsyncMock(return_value="The plan costs $75.00!")

    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)

    wf = ChatResponseWorkflow(
        knowledge_repo=knowledge_repo,
        ai_provider=ai_provider,
        cache=cache,
        tone_service=ToneAlignmentService(),
        pricing_service=PricingValidationService(),
    )

    messages = [MessageContent(text="Price?", role=MessageRole.USER)]
    result = await wf.execute(messages, "Price?")

    assert result.requires_handoff
    assert "lower than source" in result.handoff_reason
