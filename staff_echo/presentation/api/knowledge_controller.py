"""
Knowledge Controller — REST endpoints for knowledge retrieval.

Architectural Intent:
- Exposes knowledge search for the chat interface and admin tools
- Delegates to SearchKnowledgeQuery
"""

from fastapi import APIRouter, Request

from staff_echo.application.dtos.knowledge_dto import SearchKnowledgeRequest, KnowledgeEntryDTO

knowledge_router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@knowledge_router.post("/search", response_model=list[KnowledgeEntryDTO])
async def search_knowledge(request: SearchKnowledgeRequest, req: Request):
    container = req.app.state.container
    query = container.search_knowledge_query
    return await query.execute(request)
