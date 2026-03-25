"""
Transcript MCP Server — bounded context server for transcript processing.

Architectural Intent:
- Exposes transcript pipeline capabilities via MCP
- Tools: process_transcript, approve_transcript (write operations)
- Resources: transcript data, pending list (read operations)
"""

from mcp.server import Server
from mcp.types import Tool, Resource, TextContent

from staff_echo.application.commands.process_transcript import ProcessTranscriptUseCase
from staff_echo.application.commands.approve_transcript import ApproveTranscriptUseCase
from staff_echo.application.queries.get_transcript_status import GetTranscriptStatusQuery
from staff_echo.application.dtos.transcript_dto import (
    ProcessTranscriptRequest,
    ApproveTranscriptRequest,
)

import json


def create_transcript_server(
    process_use_case: ProcessTranscriptUseCase,
    approve_use_case: ApproveTranscriptUseCase,
    status_query: GetTranscriptStatusQuery,
) -> Server:
    """Factory creating the staff-echo-transcript MCP server."""
    server = Server("staff-echo-transcript")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="process_transcript",
                description="Process an audio file into a diarized, PII-masked transcript.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "audio_source": {
                            "type": "string",
                            "description": "BigQuery reference or GCS URI for the audio file",
                        },
                    },
                    "required": ["audio_source"],
                },
            ),
            Tool(
                name="approve_transcript",
                description="Approve a processed transcript for use as training data.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "transcript_id": {"type": "string", "description": "Transcript ID to approve"},
                        "approved_by": {"type": "string", "description": "Reviewer identifier"},
                    },
                    "required": ["transcript_id", "approved_by"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "process_transcript":
            request = ProcessTranscriptRequest(audio_source=arguments["audio_source"])
            result = await process_use_case.execute(request)
            return [TextContent(type="text", text=result.model_dump_json())]

        elif name == "approve_transcript":
            request = ApproveTranscriptRequest(
                transcript_id=arguments["transcript_id"],
                approved_by=arguments["approved_by"],
            )
            result = await approve_use_case.execute(request)
            return [TextContent(type="text", text=result.model_dump_json())]

        raise ValueError(f"Unknown tool: {name}")

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return [
            Resource(
                uri="transcript://{transcript_id}",
                name="Transcript",
                description="Read-only access to a transcript",
                mimeType="application/json",
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        if uri.startswith("transcript://"):
            transcript_id = uri.replace("transcript://", "")
            result = await status_query.execute(transcript_id)
            if result:
                return result.model_dump_json()
            return '{"error": "Transcript not found"}'
        raise ValueError(f"Unknown resource: {uri}")

    return server
