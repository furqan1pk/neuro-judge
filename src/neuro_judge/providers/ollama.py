"""Ollama provider for local/open-source models."""

from __future__ import annotations

import time

import httpx

from ..models import LLMResponse
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    """Local models via Ollama API."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(model)
        self.base_url = base_url

    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        image_url: str | None = None,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if image_url:
            import base64
            async with httpx.AsyncClient() as http:
                img_resp = await http.get(image_url)
                payload["images"] = [base64.b64encode(img_resp.content).decode()]

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
        latency = (time.perf_counter() - start) * 1000

        data = resp.json()
        return LLMResponse(
            text=data.get("response", ""),
            input_tokens=data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            latency_ms=round(latency, 1),
            model=self.model,
            provider="ollama",
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return 0.0  # local models are free
