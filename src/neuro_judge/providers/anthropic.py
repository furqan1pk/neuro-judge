"""Anthropic (Claude) provider."""

from __future__ import annotations

import time

import anthropic

from ..models import LLMResponse
from .base import BaseProvider

# Pricing per 1M tokens (as of 2025)
ANTHROPIC_PRICING = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
}


class AnthropicProvider(BaseProvider):
    """Claude via Anthropic API."""

    def __init__(self, model: str = "claude-sonnet-4-6", **kwargs):
        super().__init__(model)
        self.client = anthropic.AsyncAnthropic()

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        image_url: str | None = None,
    ) -> LLMResponse:
        content = []
        if image_url:
            content.append({
                "type": "image",
                "source": {"type": "url", "url": image_url},
            })
        content.append({"type": "text", "text": prompt})

        start = time.perf_counter()
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system else anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": content}],
        )
        latency = (time.perf_counter() - start) * 1000

        return LLMResponse(
            text=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=round(latency, 1),
            model=self.model,
            provider="anthropic",
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = ANTHROPIC_PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
