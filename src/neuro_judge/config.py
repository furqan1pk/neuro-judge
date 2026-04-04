"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .models import ConsensusMethod


class JudgeConfig(BaseModel):
    provider: str  # "anthropic", "openai", "gemini", "ollama"
    model: str  # "claude-sonnet-4-6", "gpt-4o", etc.
    temperature: float = 0.0
    max_tokens: int = 1024


class EvalConfig(BaseModel):
    """Top-level evaluation configuration."""

    data_path: str
    judges: list[JudgeConfig]
    criteria: list[str] = Field(default_factory=lambda: ["accuracy", "relevance", "coherence"])
    template: str | None = None  # "rag-accuracy", "summarization", "safety", "general"
    consensus: ConsensusMethod = ConsensusMethod.MEAN
    concurrency: int = 5
    output_dir: str = "./reports"
    multimodal: bool = False  # enable image evaluation


def load_config(path: str | Path) -> EvalConfig:
    """Load and validate config from YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    return EvalConfig(**raw)


def generate_default_config(template: str | None = None) -> str:
    """Generate a default YAML config string."""
    config = {
        "data_path": "sample_data.jsonl",
        "judges": [
            {"provider": "anthropic", "model": "claude-sonnet-4-6", "temperature": 0.0},
        ],
        "criteria": ["accuracy", "relevance", "coherence"],
        "consensus": "mean",
        "concurrency": 5,
        "output_dir": "./reports",
    }

    if template:
        from .templates import get_template
        tmpl = get_template(template)
        config["criteria"] = tmpl.criteria_names
        config["template"] = template

    return yaml.dump(config, default_flow_style=False, sort_keys=False)
