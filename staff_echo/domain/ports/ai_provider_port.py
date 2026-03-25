from __future__ import annotations
"""AI Provider Port — defines the contract for LLM interaction."""

from collections.abc import AsyncGenerator
from typing import Protocol

from staff_echo.domain.value_objects.message_content import MessageContent
from staff_echo.domain.value_objects.tone_profile import ToneProfile


class AIProviderPort(Protocol):
    async def generate_response(
        self,
        messages: list[MessageContent],
        context: str,
        tone_profile: ToneProfile | None = None,
    ) -> AsyncGenerator[str, None]: ...

    async def generate_response_full(
        self,
        messages: list[MessageContent],
        context: str,
        tone_profile: ToneProfile | None = None,
    ) -> str: ...
