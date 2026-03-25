"""
FastAPI Application Factory

Architectural Intent:
- Creates the FastAPI application with all routes wired to the DI container
- CORS configured for frontend development
- Lifespan context manager for startup/shutdown
- Presentation layer only interacts with application layer use cases
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from staff_echo.infrastructure.config.dependency_injection import Container
from staff_echo.presentation.api.chat_controller import chat_router
from staff_echo.presentation.api.transcript_controller import transcript_router
from staff_echo.presentation.api.knowledge_controller import knowledge_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app(container: Container) -> FastAPI:
    app = FastAPI(
        title="Staff-Echo AI Chatbot",
        description="Customer-facing chatbot trained on staff voice data",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    app.include_router(transcript_router)
    app.include_router(knowledge_router)

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "staff-echo"}

    return app
