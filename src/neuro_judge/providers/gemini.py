"""Google Gemini provider."""

from __future__ import annotations

import time

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai

from ..models import LLMResponse
from .base import BaseProvider

GEMINI_PRICING = {
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
}


class GeminiProvider(BaseProvider):
    """Gemini via Google Generative AI SDK."""

    def __init__(self, model: str = "gemini-2.0-flash", **kwargs):
        super().__init__(model)
        self._model = genai.GenerativeModel(model)

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        image_url: str | None = None,
    ) -> LLMResponse:
        parts = []
        if image_url:
            import httpx
            img_data = httpx.get(image_url).content
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_data}})

        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        parts.append(full_prompt)

        start = time.perf_counter()
        response = await self._model.generate_content_async(
            parts,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        latency = (time.perf_counter() - start) * 1000

        usage = response.usage_metadata
        return LLMResponse(
            text=response.text or "",
            input_tokens=usage.prompt_token_count if usage else 0,
            output_tokens=usage.candidates_token_count if usage else 0,
            latency_ms=round(latency, 1),
            model=self.model,
            provider="gemini",
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = GEMINI_PRICING.get(self.model, {"input": 0.10, "output": 0.40})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
