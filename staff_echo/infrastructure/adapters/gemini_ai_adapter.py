from __future__ import annotations
"""
Gemini AI Adapter — implements AIProviderPort via Google Gemini API.

Architectural Intent:
- Infrastructure adapter wrapping the Gemini 1.5 Pro model
- Builds prompts incorporating tone profile instructions
- Supports both streaming and full response generation
- Graceful degradation if SDK not installed
"""

from collections.abc import AsyncGenerator

from staff_echo.domain.value_objects.message_content import MessageContent, MessageRole
from staff_echo.domain.value_objects.tone_profile import ToneProfile

try:
    import google.generativeai as genai

    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False


class GeminiAIAdapter:

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self._api_key = api_key
        self._model_name = model
        self._model = None
        if _HAS_GENAI and api_key:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(model)

    async def generate_response(
        self,
        messages: list[MessageContent],
        context: str,
        tone_profile: ToneProfile | None = None,
    ) -> AsyncGenerator[str, None]:
        prompt = self._build_prompt(messages, context, tone_profile)

        if self._model:
            response = await self._model.generate_content_async(
                prompt, stream=True
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        else:
            # Fallback for development without API key
            fallback = self._dev_fallback(messages, context)
            for word in fallback.split(" "):
                yield word + " "

    async def generate_response_full(
        self,
        messages: list[MessageContent],
        context: str,
        tone_profile: ToneProfile | None = None,
    ) -> str:
        prompt = self._build_prompt(messages, context, tone_profile)

        if self._model:
            response = await self._model.generate_content_async(prompt)
            return response.text
        else:
            return self._dev_fallback(messages, context)

    def _build_prompt(
        self,
        messages: list[MessageContent],
        context: str,
        tone_profile: ToneProfile | None,
    ) -> str:
        parts = [
            "You are a helpful customer service assistant for Staff-Echo.",
            "Your responses should be accurate, helpful, and match the company's communication style.",
            "",
        ]

        if tone_profile:
            parts.append("COMMUNICATION STYLE INSTRUCTIONS:")
            parts.append(f"- Greeting style: {tone_profile.greeting_style}")
            parts.append(f"- Formality: {tone_profile.formality_level}")
            if tone_profile.common_phrases:
                parts.append(
                    f"- Use these phrases naturally: {', '.join(tone_profile.common_phrases)}"
                )
            parts.append("")

        parts.append("CONTEXT FROM KNOWLEDGE BASE:")
        parts.append(context)
        parts.append("")

        parts.append("IMPORTANT RULES:")
        parts.append("- Only quote prices that appear in the context above.")
        parts.append("- If you're unsure about pricing, say you'll connect them with a team member.")
        parts.append("- Be conversational but accurate.")
        parts.append("")

        parts.append("CONVERSATION HISTORY:")
        for msg in messages:
            role = "Customer" if msg.role == MessageRole.USER else "Assistant"
            parts.append(f"{role}: {msg.text}")
        parts.append("")
        parts.append("Assistant:")

        return "\n".join(parts)

    def _dev_fallback(self, messages: list[MessageContent], context: str) -> str:
        last_msg = messages[-1].text if messages else ""
        return (
            f"Thank you for your question about '{last_msg}'. "
            "Based on our records, I can help you with that. "
            "This is a development response — connect a Gemini API key for production use."
        )
