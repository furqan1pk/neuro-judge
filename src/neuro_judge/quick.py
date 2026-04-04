"""One-liner quick evaluation API."""

from __future__ import annotations

import asyncio

from .config import EvalConfig, JudgeConfig
from .models import EvalRun
from .pipeline import run_pipeline


def quick_eval(
    data: str,
    criteria: str | list[str] = "accuracy",
    judge: str = "claude-sonnet-4-6",
    provider: str = "anthropic",
) -> EvalRun:
    """Run a quick evaluation with minimal configuration.

    Usage:
        from neuro_judge import quick_eval
        results = quick_eval("outputs.jsonl", criteria="accuracy", judge="claude-sonnet-4-6")
        print(results.summary)
    """
    if isinstance(criteria, str):
        criteria = [criteria]

    config = EvalConfig(
        data_path=data,
        judges=[JudgeConfig(provider=provider, model=judge)],
        criteria=criteria,
    )

    return asyncio.run(run_pipeline(config))
