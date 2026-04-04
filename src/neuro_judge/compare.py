"""A/B comparison of two prompt versions."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from .config import EvalConfig
from .consensus import aggregate_scores
from .criteria import get_criteria
from .judge import run_judge
from .models import CompareResult, EvalRun, EvalSample
from .providers import get_provider


def load_paired_data(path_a: str, path_b: str) -> list[tuple[EvalSample, EvalSample]]:
    """Load two JSONL files and pair samples by index."""

    def _load(path: str) -> list[EvalSample]:
        samples = []
        with open(path) as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if "id" not in data:
                    data["id"] = f"sample_{i}"
                samples.append(EvalSample(**data))
        return samples

    samples_a = _load(path_a)
    samples_b = _load(path_b)

    if len(samples_a) != len(samples_b):
        raise ValueError(f"Files have different sample counts: {len(samples_a)} vs {len(samples_b)}")

    return list(zip(samples_a, samples_b))


async def run_comparison(config: EvalConfig, path_a: str, path_b: str) -> tuple[EvalRun, EvalRun, list[CompareResult]]:
    """Run evaluation on both versions and produce comparison."""
    from .pipeline import run_pipeline

    # Run both versions with same config
    config_a = config.model_copy()
    config_a.data_path = path_a
    config_b = config.model_copy()
    config_b.data_path = path_b

    run_a, run_b = await asyncio.gather(
        run_pipeline(config_a),
        run_pipeline(config_b),
    )

    # Build comparison results
    comparisons = []
    for result_a, result_b in zip(run_a.results, run_b.results):
        # Determine winner per criterion and overall
        wins_a, wins_b = 0, 0
        for criterion in config.criteria:
            score_a = result_a.scores_by_criterion.get(criterion, 0)
            score_b = result_b.scores_by_criterion.get(criterion, 0)
            if score_a > score_b:
                wins_a += 1
            elif score_b > score_a:
                wins_b += 1

        winner = "a" if wins_a > wins_b else "b" if wins_b > wins_a else "tie"

        comparisons.append(CompareResult(
            sample_id=result_a.sample_id,
            input=result_a.input,
            output_a=result_a.output,
            output_b=result_b.output,
            scores_a=result_a.scores_by_criterion,
            scores_b=result_b.scores_by_criterion,
            winner=winner,
        ))

    return run_a, run_b, comparisons
