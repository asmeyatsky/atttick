"""
Dependency Injection Container — Composition Root

Architectural Intent:
- Wires all adapters to their ports at application startup
- Provides factory methods for production and development configurations
- Lazy singleton creation for all components
- Single place where infrastructure touches domain contracts
"""

from staff_echo.domain.services.pii_masking_service import PIIMaskingService
from staff_echo.domain.services.tone_alignment_service import ToneAlignmentService
from staff_echo.domain.services.pricing_validation_service import PricingValidationService

from staff_echo.infrastructure.config.settings import Settings
from staff_echo.infrastructure.repositories.in_memory_conversation_repo import InMemoryConversationRepository
from staff_echo.infrastructure.repositories.in_memory_transcript_repo import InMemoryTranscriptRepository
from staff_echo.infrastructure.repositories.in_memory_knowledge_repo import InMemoryKnowledgeRepository
from staff_echo.infrastructure.adapters.gemini_ai_adapter import GeminiAIAdapter
from staff_echo.infrastructure.adapters.google_stt_adapter import GoogleSTTAdapter
from staff_echo.infrastructure.adapters.in_memory_cache_adapter import InMemoryCacheAdapter
from staff_echo.infrastructure.adapters.in_memory_event_bus import InMemoryEventBus
from staff_echo.infrastructure.pii.regex_pii_detector import RegexPIIDetector

from staff_echo.application.commands.send_message import SendMessageUseCase
from staff_echo.application.commands.send_message_streaming import SendMessageStreamingUseCase
from staff_echo.application.commands.process_transcript import ProcessTranscriptUseCase
from staff_echo.application.commands.approve_transcript import ApproveTranscriptUseCase
from staff_echo.application.commands.handoff_to_human import HandoffToHumanUseCase
from staff_echo.application.queries.get_conversation import GetConversationQuery
from staff_echo.application.queries.search_knowledge import SearchKnowledgeQuery
from staff_echo.application.queries.get_transcript_status import GetTranscriptStatusQuery


class Container:
    """DI container that lazily creates and caches singletons."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._instances: dict[type, object] = {}

    def _get_or_create(self, cls: type, factory):
        if cls not in self._instances:
            self._instances[cls] = factory()
        return self._instances[cls]

    # --- Repositories ---

    @property
    def conversation_repo(self) -> InMemoryConversationRepository:
        return self._get_or_create(
            InMemoryConversationRepository, InMemoryConversationRepository
        )

    @property
    def transcript_repo(self) -> InMemoryTranscriptRepository:
        return self._get_or_create(
            InMemoryTranscriptRepository, InMemoryTranscriptRepository
        )

    @property
    def knowledge_repo(self) -> InMemoryKnowledgeRepository:
        return self._get_or_create(
            InMemoryKnowledgeRepository, InMemoryKnowledgeRepository
        )

    # --- Adapters ---

    @property
    def ai_provider(self) -> GeminiAIAdapter:
        return self._get_or_create(
            GeminiAIAdapter,
            lambda: GeminiAIAdapter(
                api_key=self.settings.gemini_api_key,
                model=self.settings.gemini_model,
            ),
        )

    @property
    def transcription(self) -> GoogleSTTAdapter:
        return self._get_or_create(
            GoogleSTTAdapter,
            lambda: GoogleSTTAdapter(project_id=self.settings.bigquery_project),
        )

    @property
    def cache(self) -> InMemoryCacheAdapter:
        return self._get_or_create(InMemoryCacheAdapter, InMemoryCacheAdapter)

    @property
    def event_bus(self) -> InMemoryEventBus:
        return self._get_or_create(InMemoryEventBus, InMemoryEventBus)

    @property
    def pii_detector(self) -> RegexPIIDetector:
        return self._get_or_create(RegexPIIDetector, RegexPIIDetector)

    # --- Domain Services ---

    @property
    def pii_masking_service(self) -> PIIMaskingService:
        return self._get_or_create(PIIMaskingService, PIIMaskingService)

    @property
    def tone_alignment_service(self) -> ToneAlignmentService:
        return self._get_or_create(ToneAlignmentService, ToneAlignmentService)

    @property
    def pricing_validation_service(self) -> PricingValidationService:
        return self._get_or_create(PricingValidationService, PricingValidationService)

    # --- Use Cases ---

    @property
    def send_message_use_case(self) -> SendMessageUseCase:
        return self._get_or_create(
            SendMessageUseCase,
            lambda: SendMessageUseCase(
                conversation_repo=self.conversation_repo,
                knowledge_repo=self.knowledge_repo,
                ai_provider=self.ai_provider,
                cache=self.cache,
                event_bus=self.event_bus,
                tone_service=self.tone_alignment_service,
                pricing_service=self.pricing_validation_service,
            ),
        )

    @property
    def send_message_streaming_use_case(self) -> SendMessageStreamingUseCase:
        return self._get_or_create(
            SendMessageStreamingUseCase,
            lambda: SendMessageStreamingUseCase(
                conversation_repo=self.conversation_repo,
                knowledge_repo=self.knowledge_repo,
                ai_provider=self.ai_provider,
                cache=self.cache,
                event_bus=self.event_bus,
                tone_service=self.tone_alignment_service,
                pricing_service=self.pricing_validation_service,
            ),
        )

    @property
    def process_transcript_use_case(self) -> ProcessTranscriptUseCase:
        return self._get_or_create(
            ProcessTranscriptUseCase,
            lambda: ProcessTranscriptUseCase(
                transcript_repo=self.transcript_repo,
                transcription=self.transcription,
                pii_detector=self.pii_detector,
                pii_service=self.pii_masking_service,
                event_bus=self.event_bus,
            ),
        )

    @property
    def approve_transcript_use_case(self) -> ApproveTranscriptUseCase:
        return self._get_or_create(
            ApproveTranscriptUseCase,
            lambda: ApproveTranscriptUseCase(
                transcript_repo=self.transcript_repo,
                knowledge_repo=self.knowledge_repo,
                event_bus=self.event_bus,
            ),
        )

    @property
    def handoff_use_case(self) -> HandoffToHumanUseCase:
        return self._get_or_create(
            HandoffToHumanUseCase,
            lambda: HandoffToHumanUseCase(
                conversation_repo=self.conversation_repo,
                event_bus=self.event_bus,
            ),
        )

    # --- Queries ---

    @property
    def get_conversation_query(self) -> GetConversationQuery:
        return self._get_or_create(
            GetConversationQuery,
            lambda: GetConversationQuery(conversation_repo=self.conversation_repo),
        )

    @property
    def search_knowledge_query(self) -> SearchKnowledgeQuery:
        return self._get_or_create(
            SearchKnowledgeQuery,
            lambda: SearchKnowledgeQuery(
                knowledge_repo=self.knowledge_repo, cache=self.cache
            ),
        )

    @property
    def get_transcript_status_query(self) -> GetTranscriptStatusQuery:
        return self._get_or_create(
            GetTranscriptStatusQuery,
            lambda: GetTranscriptStatusQuery(transcript_repo=self.transcript_repo),
        )


def create_development_container() -> Container:
    return Container(Settings())


def create_production_container(settings: Settings) -> Container:
    return Container(settings)
