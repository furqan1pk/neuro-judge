"""Core data models for neuro-judge."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ConsensusMethod(str, Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MAJORITY_VOTE = "majority_vote"


class Criterion(BaseModel):
    """A scoring dimension for evaluation."""

    name: str
    description: str
    scale_min: int = 1
    scale_max: int = 5
    weight: float = 1.0


class EvalSample(BaseModel):
    """One input/output pair to evaluate."""

    id: str
    input: str
    output: str
    reference: str | None = None
    image_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    model: str
    provider: str


class JudgeScore(BaseModel):
    """One judge's score on one sample for one criterion."""

    sample_id: str
    criterion: str
    judge_model: str
    judge_provider: str
    score: int
    reasoning: str
    latency_ms: float
    cost_usd: float


class EvalResult(BaseModel):
    """Aggregated result for one sample across all judges."""

    sample_id: str
    input: str
    output: str
    reference: str | None = None
    scores_by_criterion: dict[str, float]  # criterion_name -> consensus score
    judge_scores: list[JudgeScore]  # raw individual scores
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompareResult(BaseModel):
    """Comparison of two versions for one sample."""

    sample_id: str
    input: str
    output_a: str
    output_b: str
    scores_a: dict[str, float]
    scores_b: dict[str, float]
    winner: str  # "a", "b", or "tie"


class EvalRun(BaseModel):
    """Complete evaluation run with all results."""

    run_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    config_summary: dict[str, Any] = Field(default_factory=dict)
    criteria: list[Criterion]
    judges: list[str]
    results: list[EvalResult]
    total_samples: int = 0
    total_cost_usd: float = 0.0
    total_time_seconds: float = 0.0
    summary: dict[str, float] = Field(default_factory=dict)  # criterion -> mean score
