"""OpenAI (GPT) provider."""

from __future__ import annotations

import time

import openai

from ..models import LLMResponse
from .base import BaseProvider

OPENAI_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
}


class OpenAIProvider(BaseProvider):
    """GPT via OpenAI API."""

    def __init__(self, model: str = "gpt-4o", **kwargs):
        super().__init__(model)
        self.client = openai.AsyncOpenAI()

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        image_url: str | None = None,
    ) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            })
        else:
            messages.append({"role": "user", "content": prompt})

        start = time.perf_counter()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = (time.perf_counter() - start) * 1000

        usage = response.usage
        return LLMResponse(
            text=response.choices[0].message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            latency_ms=round(latency, 1),
            model=self.model,
            provider="openai",
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = OPENAI_PRICING.get(self.model, {"input": 2.50, "output": 10.00})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
