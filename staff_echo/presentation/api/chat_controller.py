from __future__ import annotations
"""
Chat Controller — REST and WebSocket endpoints for chat interactions.

Architectural Intent:
- Presentation layer that delegates to application use cases
- POST /send for synchronous chat responses
- WebSocket /ws/{conversation_id} for streaming responses per PRD requirement
- GET /conversations/{id} for reading conversation history
"""

import json

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from staff_echo.application.dtos.chat_dto import SendMessageRequest, SendMessageResponse, ConversationDTO

chat_router = APIRouter(prefix="/api/chat", tags=["chat"])


@chat_router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, req: Request):
    container = req.app.state.container
    use_case = container.send_message_use_case
    return await use_case.execute(request)


@chat_router.get("/conversations/{conversation_id}", response_model=ConversationDTO | None)
async def get_conversation(conversation_id: str, req: Request):
    container = req.app.state.container
    query = container.get_conversation_query
    result = await query.execute(conversation_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


class HandoffRequest(BaseModel):
    conversation_id: str
    reason: str


@chat_router.post("/handoff", response_model=ConversationDTO)
async def handoff_to_human(request: HandoffRequest, req: Request):
    container = req.app.state.container
    use_case = container.handoff_use_case
    return await use_case.execute(request.conversation_id, request.reason)


@chat_router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    container = websocket.app.state.container
    use_case = container.send_message_streaming_use_case

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            request = SendMessageRequest(
                conversation_id=conversation_id,
                customer_id=msg.get("customer_id", "anonymous"),
                message=msg["message"],
            )

            async for chunk in use_case.execute(request):
                await websocket.send_text(chunk.model_dump_json())

    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close(code=1011)
