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

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
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
            "You are a customer support assistant for Attraction Tickets (attractiontickets.com),",
            "the UK's number 1 attraction ticket provider.",
            "Your personality and knowledge come from real staff phone conversations that have been",
            "transcribed and analyzed. You speak the way our team speaks — friendly, helpful, and knowledgeable.",
            "Customers should feel like they're talking to a real Attraction Tickets team member.",
            "",
        ]

        if tone_profile:
            parts.append("YOUR COMMUNICATION STYLE (learned from staff recordings):")
            parts.append(f"- Greeting style: {tone_profile.greeting_style}")
            parts.append(f"- Tone: {tone_profile.formality_level} and approachable")
            if tone_profile.common_phrases:
                parts.append(
                    f"- Phrases our staff commonly use: {', '.join(tone_profile.common_phrases)}"
                )
            if tone_profile.analogies:
                parts.append(
                    f"- Staff analogies you can use: {', '.join(tone_profile.analogies)}"
                )
            parts.append("- Weave these phrases in naturally, don't force them into every response.")
            parts.append("")

        parts.append("KNOWLEDGE BASE (sourced from staff recordings and BigQuery):")
        parts.append(context)
        parts.append("")

        parts.append("IMPORTANT RULES:")
        parts.append("- Only quote prices that appear in the context above. Never invent pricing.")
        parts.append("- If asked about pricing not in the context, say you'll connect them with a team member.")
        parts.append("- Be conversational, warm, and helpful — like a real Attraction Tickets team member on the phone.")
        parts.append("- Keep responses concise (2-4 sentences) unless the customer asks for detail.")
        parts.append("- When relevant, mention that tickets are cheaper when booked in advance through us.")
        parts.append("")

        parts.append("CONVERSATION:")
        for msg in messages:
            role = "Customer" if msg.role == MessageRole.USER else "Attraction Tickets Assistant"
            parts.append(f"{role}: {msg.text}")
        parts.append("")
        parts.append("Attraction Tickets Assistant:")

        return "\n".join(parts)

    def _dev_fallback(self, messages: list[MessageContent], context: str) -> str:
        last_msg = messages[-1].text if messages else ""
        return (
            f"Thank you for your question about '{last_msg}'. "
            "Based on our records, I can help you with that. "
            "This is a development response — connect a Gemini API key for production use."
        )
