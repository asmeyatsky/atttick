"""
Chat MCP Server — bounded context server for conversation management.

Architectural Intent:
- Exposes chat capabilities via Model Context Protocol
- Tools for write operations: send_message, handoff_to_human
- Resources for read operations: conversation data
- Prompts for reusable interaction patterns
- Wraps application use cases — no business logic here
"""

from mcp.server import Server
from mcp.types import Tool, Resource, TextContent

from staff_echo.application.commands.send_message import SendMessageUseCase
from staff_echo.application.commands.handoff_to_human import HandoffToHumanUseCase
from staff_echo.application.queries.get_conversation import GetConversationQuery
from staff_echo.application.dtos.chat_dto import SendMessageRequest


def create_chat_server(
    send_message_use_case: SendMessageUseCase,
    handoff_use_case: HandoffToHumanUseCase,
    get_conversation_query: GetConversationQuery,
) -> Server:
    """Factory creating the staff-echo-chat MCP server."""
    server = Server("staff-echo-chat")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="send_message",
                description="Send a customer message and get an AI response with staff-like tone.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "Customer identifier"},
                        "message": {"type": "string", "description": "Customer message text"},
                        "conversation_id": {"type": "string", "description": "Existing conversation ID (optional)"},
                    },
                    "required": ["customer_id", "message"],
                },
            ),
            Tool(
                name="handoff_to_human",
                description="Escalate a conversation to a human agent.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string", "description": "Conversation to escalate"},
                        "reason": {"type": "string", "description": "Reason for handoff"},
                    },
                    "required": ["conversation_id", "reason"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "send_message":
            request = SendMessageRequest(
                customer_id=arguments["customer_id"],
                message=arguments["message"],
                conversation_id=arguments.get("conversation_id"),
            )
            result = await send_message_use_case.execute(request)
            return [TextContent(type="text", text=result.model_dump_json())]

        elif name == "handoff_to_human":
            result = await handoff_use_case.execute(
                arguments["conversation_id"], arguments["reason"]
            )
            return [TextContent(type="text", text=result.model_dump_json())]

        raise ValueError(f"Unknown tool: {name}")

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return [
            Resource(
                uri="conversation://{conversation_id}",
                name="Conversation",
                description="Read-only access to a conversation",
                mimeType="application/json",
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        if uri.startswith("conversation://"):
            conversation_id = uri.replace("conversation://", "")
            result = await get_conversation_query.execute(conversation_id)
            if result:
                return result.model_dump_json()
            return '{"error": "Conversation not found"}'
        raise ValueError(f"Unknown resource: {uri}")

    return server
