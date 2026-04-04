"""HTML report generation with Chart.js."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from ..cost import cost_by_model
from ..models import EvalRun

TEMPLATE_PATH = Path(__file__).parent / "template.html"


def render_html(eval_run: EvalRun, output_dir: Path) -> Path:
    """Render HTML report from evaluation run."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare chart data
    criteria_names = list(eval_run.summary.keys())
    criteria_scores = list(eval_run.summary.values())

    # Score distribution per criterion
    score_distributions = {}
    for criterion in criteria_names:
        dist = [0, 0, 0, 0, 0]  # scores 1-5
        for result in eval_run.results:
            for js in result.judge_scores:
                if js.criterion == criterion and 1 <= js.score <= 5:
                    dist[js.score - 1] += 1
        score_distributions[criterion] = dist

    # Cost breakdown
    all_scores = [js for r in eval_run.results for js in r.judge_scores]
    cost_breakdown = cost_by_model(all_scores)

    # Judge agreement per criterion
    judge_means = {}
    for judge in eval_run.judges:
        judge_means[judge] = {}
        for criterion in criteria_names:
            scores = [
                js.score for r in eval_run.results for js in r.judge_scores
                if js.criterion == criterion and f"{js.judge_provider}/{js.judge_model}" == judge
            ]
            judge_means[judge][criterion] = round(sum(scores) / len(scores), 2) if scores else 0

    template = Template(TEMPLATE_PATH.read_text())
    html = template.render(
        run=eval_run,
        criteria_names=criteria_names,
        criteria_scores=criteria_scores,
        score_distributions=score_distributions,
        cost_breakdown=cost_breakdown,
        judge_means=judge_means,
    )

    path = output_dir / f"eval_{eval_run.run_id}.html"
    path.write_text(html)
    return path
