"""Cost tracking and summarization."""

from __future__ import annotations

from .models import JudgeScore


def total_cost(scores: list[JudgeScore]) -> float:
    """Sum total cost across all judge scores."""
    return round(sum(s.cost_usd for s in scores), 6)


def cost_by_model(scores: list[JudgeScore]) -> dict[str, float]:
    """Break down cost by model."""
    breakdown: dict[str, float] = {}
    for s in scores:
        key = f"{s.judge_provider}/{s.judge_model}"
        breakdown[key] = breakdown.get(key, 0.0) + s.cost_usd
    return {k: round(v, 6) for k, v in breakdown.items()}


def cost_by_criterion(scores: list[JudgeScore]) -> dict[str, float]:
    """Break down cost by criterion."""
    breakdown: dict[str, float] = {}
    for s in scores:
        breakdown[s.criterion] = breakdown.get(s.criterion, 0.0) + s.cost_usd
    return {k: round(v, 6) for k, v in breakdown.items()}
