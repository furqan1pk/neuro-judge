"""JSON report output."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import EvalRun


def save_json(eval_run: EvalRun, output_dir: Path) -> Path:
    """Save evaluation run as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"eval_{eval_run.run_id}.json"
    path.write_text(eval_run.model_dump_json(indent=2))
    return path
