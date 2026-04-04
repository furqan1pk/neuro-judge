"""Pre-built evaluation templates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalTemplate:
    name: str
    description: str
    criteria_names: list[str]


TEMPLATES: dict[str, EvalTemplate] = {
    "general": EvalTemplate(
        name="general",
        description="General quality evaluation",
        criteria_names=["accuracy", "relevance", "coherence"],
    ),
    "rag-accuracy": EvalTemplate(
        name="rag-accuracy",
        description="RAG pipeline evaluation — faithfulness, relevance, completeness",
        criteria_names=["faithfulness", "relevance", "completeness"],
    ),
    "summarization": EvalTemplate(
        name="summarization",
        description="Summary quality — completeness, conciseness, faithfulness",
        criteria_names=["completeness", "conciseness", "faithfulness"],
    ),
    "safety": EvalTemplate(
        name="safety",
        description="Safety and toxicity checking",
        criteria_names=["safety", "helpfulness"],
    ),
}


def get_template(name: str) -> EvalTemplate:
    """Get a template by name."""
    if name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown template '{name}'. Available: {available}")
    return TEMPLATES[name]


def list_templates() -> list[EvalTemplate]:
    """List all available templates."""
    return list(TEMPLATES.values())
