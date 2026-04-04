"""neuro-judge: LLM-as-a-Judge evaluation framework."""

from .models import EvalRun, EvalSample, Criterion, JudgeScore, EvalResult
from .pipeline import run_pipeline
from .quick import quick_eval
from .config import EvalConfig, load_config

__version__ = "0.1.0"
__all__ = [
    "EvalRun",
    "EvalSample",
    "Criterion",
    "JudgeScore",
    "EvalResult",
    "EvalConfig",
    "run_pipeline",
    "quick_eval",
    "load_config",
]
