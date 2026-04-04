"""Abstract base provider for LLM APIs."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import LLMResponse


class BaseProvider(ABC):
    """Abstract LLM provider interface."""

    def __init__(self, model: str, **kwargs):
        self.model = model

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        image_url: str | None = None,
    ) -> LLMResponse:
        """Send a completion request to the LLM."""
        ...

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for a given token count."""
        ...
