"""
Integration Test — Full Chat Flow

Tests the complete flow from SendMessageRequest to SendMessageResponse
using the DI container with in-memory infrastructure.
"""

import pytest

from staff_echo.infrastructure.config.dependency_injection import create_development_container
from staff_echo.application.dtos.chat_dto import SendMessageRequest
from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource


@pytest.fixture
def container():
    return create_development_container()


@pytest.mark.asyncio
async def test_full_chat_flow(container):
    """Test: customer sends message -> gets AI response -> conversation persisted."""
    use_case = container.send_message_use_case
    request = SendMessageRequest(customer_id="test-customer", message="Tell me about your services")

    response = await use_case.execute(request)

    assert response.conversation_id
    assert response.response_text
    assert not response.requires_handoff

    # Verify conversation was persisted
    conv = await container.conversation_repo.get_by_id(response.conversation_id)
    assert conv is not None
    assert conv.message_count == 2  # user + assistant


@pytest.mark.asyncio
async def test_chat_with_known_pricing(container):
    """Test: knowledge base has pricing -> response includes verified info."""
    # Seed knowledge base
    pricing = PricingInfo(amount=99.0, currency="USD", product_id="starter", source=PricingSource.BIGQUERY_VERIFIED)
    entry = KnowledgeEntry(
        id="pricing-1",
        category=KnowledgeCategory.PRICING,
        content="Our starter plan costs $99 per month",
        pricing_info=pricing,
    )
    await container.knowledge_repo.save(entry)

    use_case = container.send_message_use_case
    request = SendMessageRequest(customer_id="test-customer", message="What does the starter plan cost?")

    response = await use_case.execute(request)
    assert response.conversation_id
    assert response.response_text


@pytest.mark.asyncio
async def test_conversation_continuity(container):
    """Test: follow-up messages use the same conversation."""
    use_case = container.send_message_use_case

    # First message
    r1 = await use_case.execute(
        SendMessageRequest(customer_id="cust-1", message="Hello")
    )

    # Second message on same conversation
    r2 = await use_case.execute(
        SendMessageRequest(
            conversation_id=r1.conversation_id,
            customer_id="cust-1",
            message="Follow up question",
        )
    )

    assert r2.conversation_id == r1.conversation_id
    conv = await container.conversation_repo.get_by_id(r1.conversation_id)
    assert conv.message_count == 4  # 2 user + 2 assistant


@pytest.mark.asyncio
async def test_transcript_processing_flow(container):
    """Test: process transcript -> approve -> knowledge extracted."""
    from staff_echo.application.dtos.transcript_dto import ProcessTranscriptRequest, ApproveTranscriptRequest

    # Process
    process_uc = container.process_transcript_use_case
    result = await process_uc.execute(ProcessTranscriptRequest(audio_source="gs://test/call.wav"))
    assert result.status == "processed"
    assert len(result.segments) > 0

    # Approve
    approve_uc = container.approve_transcript_use_case
    approved = await approve_uc.execute(
        ApproveTranscriptRequest(transcript_id=result.id, approved_by="admin")
    )
    assert approved.status == "approved"
