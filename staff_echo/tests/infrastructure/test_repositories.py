"""
Infrastructure Tests — In-Memory Repositories

Tests the in-memory repository implementations.
"""

import pytest

from staff_echo.infrastructure.repositories.in_memory_conversation_repo import InMemoryConversationRepository
from staff_echo.infrastructure.repositories.in_memory_transcript_repo import InMemoryTranscriptRepository
from staff_echo.infrastructure.repositories.in_memory_knowledge_repo import InMemoryKnowledgeRepository
from staff_echo.domain.entities.conversation import Conversation
from staff_echo.domain.entities.transcript import Transcript, TranscriptStatus
from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource


class TestInMemoryConversationRepo:

    @pytest.mark.asyncio
    async def test_save_and_retrieve(self):
        repo = InMemoryConversationRepository()
        conv = Conversation(id="c1", customer_id="cust-1")
        await repo.save(conv)

        result = await repo.get_by_id("c1")
        assert result is not None
        assert result.id == "c1"

    @pytest.mark.asyncio
    async def test_get_by_customer_id(self):
        repo = InMemoryConversationRepository()
        await repo.save(Conversation(id="c1", customer_id="cust-1"))
        await repo.save(Conversation(id="c2", customer_id="cust-1"))
        await repo.save(Conversation(id="c3", customer_id="cust-2"))

        results = await repo.get_by_customer_id("cust-1")
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        repo = InMemoryConversationRepository()
        assert await repo.get_by_id("nonexistent") is None


class TestInMemoryTranscriptRepo:

    @pytest.mark.asyncio
    async def test_save_and_get_pending(self):
        repo = InMemoryTranscriptRepository()
        t = Transcript(id="t1", audio_source="test", status=TranscriptStatus.PENDING)
        await repo.save(t)

        pending = await repo.get_pending()
        assert len(pending) == 1

    @pytest.mark.asyncio
    async def test_get_approved(self):
        repo = InMemoryTranscriptRepository()
        await repo.save(Transcript(id="t1", audio_source="a", status=TranscriptStatus.APPROVED, approved_by="rev"))
        await repo.save(Transcript(id="t2", audio_source="b", status=TranscriptStatus.PENDING))

        approved = await repo.get_approved()
        assert len(approved) == 1
        assert approved[0].id == "t1"


class TestInMemoryKnowledgeRepo:

    @pytest.mark.asyncio
    async def test_search_by_keyword(self):
        repo = InMemoryKnowledgeRepository()
        await repo.save(KnowledgeEntry(id="k1", category=KnowledgeCategory.FAQ, content="Our office hours are 9 to 5"))
        await repo.save(KnowledgeEntry(id="k2", category=KnowledgeCategory.PRICING, content="Premium plan costs $199"))

        results = await repo.search("hours")
        assert len(results) == 1
        assert results[0].id == "k1"

    @pytest.mark.asyncio
    async def test_search_with_category_filter(self):
        repo = InMemoryKnowledgeRepository()
        await repo.save(KnowledgeEntry(id="k1", category=KnowledgeCategory.FAQ, content="hours info"))
        await repo.save(KnowledgeEntry(id="k2", category=KnowledgeCategory.PRICING, content="hours pricing"))

        results = await repo.search("hours", category=KnowledgeCategory.PRICING)
        assert len(results) == 1
        assert results[0].category == KnowledgeCategory.PRICING

    @pytest.mark.asyncio
    async def test_get_pricing(self):
        repo = InMemoryKnowledgeRepository()
        pricing = PricingInfo(amount=99.0, currency="USD", product_id="basic-plan", source=PricingSource.BIGQUERY_VERIFIED)
        await repo.save(KnowledgeEntry(id="k1", category=KnowledgeCategory.PRICING, content="Basic plan", pricing_info=pricing))

        result = await repo.get_pricing("basic")
        assert len(result) == 1
        assert result[0].amount == 99.0
