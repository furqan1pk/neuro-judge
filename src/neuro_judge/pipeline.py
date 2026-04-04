"""Main evaluation pipeline orchestrator."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from pathlib import Path

from .config import EvalConfig
from .consensus import aggregate_scores
from .cost import cost_by_model, total_cost
from .criteria import get_criteria
from .judge import run_judge
from .models import ConsensusMethod, EvalResult, EvalRun, EvalSample
from .providers import get_provider


def load_data(path: str | Path) -> list[EvalSample]:
    """Load evaluation samples from JSONL file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

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


async def run_pipeline(config: EvalConfig) -> EvalRun:
    """Run the full evaluation pipeline."""
    start_time = time.perf_counter()

    # Load data and criteria
    samples = load_data(config.data_path)
    criteria = get_criteria(config.criteria)

    # Initialize providers
    providers = [get_provider(j.provider, j.model) for j in config.judges]
    judge_names = [f"{j.provider}/{j.model}" for j in config.judges]

    # Semaphore for concurrency control
    sem = asyncio.Semaphore(config.concurrency)

    async def judge_with_sem(provider, sample, criterion):
        async with sem:
            return await run_judge(provider, sample, criterion)

    # Run all judge evaluations
    all_scores = []
    tasks = []
    for sample in samples:
        for criterion in criteria:
            for provider in providers:
                tasks.append(judge_with_sem(provider, sample, criterion))

    all_scores = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    valid_scores = [s for s in all_scores if not isinstance(s, Exception)]
    errors = [s for s in all_scores if isinstance(s, Exception)]
    if errors:
        import sys
        for e in errors[:5]:
            print(f"  Judge error: {e}", file=sys.stderr)

    # Aggregate results per sample
    results = []
    for sample in samples:
        sample_scores = [s for s in valid_scores if s.sample_id == sample.id]
        scores_by_criterion = {}
        for criterion in criteria:
            criterion_scores = [s for s in sample_scores if s.criterion == criterion.name]
            scores_by_criterion[criterion.name] = aggregate_scores(criterion_scores, config.consensus)

        results.append(EvalResult(
            sample_id=sample.id,
            input=sample.input,
            output=sample.output,
            reference=sample.reference,
            scores_by_criterion=scores_by_criterion,
            judge_scores=sample_scores,
            metadata=sample.metadata,
        ))

    # Compute summary
    summary = {}
    for criterion in criteria:
        criterion_values = [r.scores_by_criterion.get(criterion.name, 0) for r in results]
        summary[criterion.name] = round(sum(criterion_values) / len(criterion_values), 2) if criterion_values else 0.0

    elapsed = time.perf_counter() - start_time

    return EvalRun(
        run_id=str(uuid.uuid4())[:8],
        criteria=criteria,
        judges=judge_names,
        results=results,
        total_samples=len(samples),
        total_cost_usd=total_cost(valid_scores),
        total_time_seconds=round(elapsed, 2),
        summary=summary,
        config_summary={
            "data_path": config.data_path,
            "consensus": config.consensus.value,
            "judges": judge_names,
            "criteria": config.criteria,
            "cost_by_model": cost_by_model(valid_scores),
        },
    )
