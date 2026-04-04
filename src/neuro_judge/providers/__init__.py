"""Provider registry."""

from __future__ import annotations

from .anthropic import AnthropicProvider
from .base import BaseProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
}


def get_provider(provider_name: str, model: str, **kwargs) -> BaseProvider:
    """Get a provider instance by name."""
    cls = PROVIDER_REGISTRY.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {list(PROVIDER_REGISTRY.keys())}")
    return cls(model=model, **kwargs)
