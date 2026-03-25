"""
Knowledge MCP Server — bounded context server for knowledge retrieval.

Architectural Intent:
- Exposes knowledge base capabilities via MCP
- Resources for search and pricing lookup (read operations)
- Tools for knowledge ingestion (write operations)
"""

from mcp.server import Server
from mcp.types import Tool, Resource, TextContent

from staff_echo.application.queries.search_knowledge import SearchKnowledgeQuery
from staff_echo.application.dtos.knowledge_dto import SearchKnowledgeRequest

import json


def create_knowledge_server(
    search_query: SearchKnowledgeQuery,
) -> Server:
    """Factory creating the staff-echo-knowledge MCP server."""
    server = Server("staff-echo-knowledge")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_knowledge",
                description="Search the knowledge base for product specs, pricing, or FAQs.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "category": {
                            "type": "string",
                            "enum": ["product_spec", "pricing", "faq", "general"],
                            "description": "Filter by category (optional)",
                        },
                        "limit": {"type": "integer", "default": 10, "description": "Max results"},
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "search_knowledge":
            request = SearchKnowledgeRequest(
                query=arguments["query"],
                category=arguments.get("category"),
                limit=arguments.get("limit", 10),
            )
            results = await search_query.execute(request)
            return [
                TextContent(
                    type="text",
                    text=json.dumps([r.model_dump() for r in results]),
                )
            ]
        raise ValueError(f"Unknown tool: {name}")

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return [
            Resource(
                uri="knowledge://search",
                name="Knowledge Search",
                description="Search knowledge entries",
                mimeType="application/json",
            ),
        ]

    return server
