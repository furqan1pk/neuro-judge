"""CLI interface for neuro-judge."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="neuro-judge")
def main():
    """neuro-judge: LLM-as-a-Judge evaluation framework."""
    pass


@main.command()
@click.option("--template", type=str, default=None, help="Eval template: general, rag-accuracy, summarization, safety")
@click.option("--dir", "output_dir", type=str, default=".", help="Directory to create files in")
def init(template: str | None, output_dir: str):
    """Initialize a new evaluation project with config and sample data."""
    from .config import generate_default_config

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Write config
    config_str = generate_default_config(template)
    config_path = out / "eval.yaml"
    config_path.write_text(config_str)

    # Write sample data
    sample_data = [
        {"id": "s1", "input": "What is the capital of France?", "output": "The capital of France is Paris.", "reference": "Paris"},
        {"id": "s2", "input": "Explain photosynthesis in one sentence.", "output": "Photosynthesis is the process by which plants convert sunlight into energy.", "reference": "Photosynthesis is the process where plants use sunlight, water, and CO2 to produce glucose and oxygen."},
        {"id": "s3", "input": "What is 2+2?", "output": "2+2 equals 4.", "reference": "4"},
        {"id": "s4", "input": "Summarize the theory of relativity.", "output": "Einstein's theory states that the laws of physics are the same for all non-accelerating observers, and the speed of light is constant regardless of the observer's motion.", "reference": "Einstein's theory of relativity includes special relativity (constant speed of light, time dilation) and general relativity (gravity as spacetime curvature)."},
        {"id": "s5", "input": "What causes rain?", "output": "Rain is caused by water evaporating, forming clouds, and then falling back down.", "reference": "Rain occurs when water vapor in the atmosphere condenses into droplets that become heavy enough to fall as precipitation."},
    ]
    data_path = out / "sample_data.jsonl"
    with open(data_path, "w") as f:
        for item in sample_data:
            f.write(json.dumps(item) + "\n")

    # Write .env.example
    env_path = out / ".env.example"
    if not env_path.exists():
        env_path.write_text("ANTHROPIC_API_KEY=sk-ant-...\nOPENAI_API_KEY=sk-...\nGOOGLE_API_KEY=...\n")

    console.print(f"[green]Created:[/green] {config_path}")
    console.print(f"[green]Created:[/green] {data_path}")
    console.print(f"[green]Created:[/green] {env_path}")
    console.print(f"\n[bold]Next:[/bold] Set your API key in .env, then run: [cyan]neuro-judge run --config {config_path}[/cyan]")


@main.command()
@click.option("--config", "config_path", required=True, help="Path to eval.yaml")
@click.option("--output-dir", default="./reports", help="Directory for reports")
@click.option("--verbose", is_flag=True, help="Show detailed progress")
def run(config_path: str, output_dir: str, verbose: bool):
    """Run evaluation pipeline and generate reports."""
    from .config import load_config
    from .pipeline import run_pipeline
    from .report.html_report import render_html
    from .report.json_report import save_json

    config = load_config(config_path)
    config.output_dir = output_dir

    console.print(f"[bold]neuro-judge[/bold] v0.1.0")
    console.print(f"  Data: {config.data_path}")
    console.print(f"  Judges: {', '.join(f'{j.provider}/{j.model}' for j in config.judges)}")
    console.print(f"  Criteria: {', '.join(config.criteria)}")
    console.print()

    with console.status("[bold cyan]Running evaluation..."):
        eval_run = asyncio.run(run_pipeline(config))

    # Save reports
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = save_json(eval_run, out)
    html_path = render_html(eval_run, out)

    # Print summary
    console.print(f"\n[bold green]Evaluation complete![/bold green]")
    table = Table(title="Results Summary")
    table.add_column("Criterion", style="cyan")
    table.add_column("Score", justify="center")
    for name, score in eval_run.summary.items():
        color = "green" if score >= 4 else "yellow" if score >= 3 else "red"
        table.add_row(name, f"[{color}]{score:.2f}[/{color}] / 5.00")
    console.print(table)

    console.print(f"\n  Samples: {eval_run.total_samples}")
    console.print(f"  Cost: ${eval_run.total_cost_usd:.4f}")
    console.print(f"  Time: {eval_run.total_time_seconds:.1f}s")
    console.print(f"\n  JSON: {json_path}")
    console.print(f"  HTML: {html_path}")


@main.command()
@click.option("--config", "config_path", required=True, help="Path to eval.yaml")
@click.option("--a", "path_a", required=True, help="JSONL for version A")
@click.option("--b", "path_b", required=True, help="JSONL for version B")
@click.option("--output-dir", default="./reports", help="Directory for reports")
def compare(config_path: str, path_a: str, path_b: str, output_dir: str):
    """Compare two prompt versions side by side."""
    from .compare import run_comparison
    from .config import load_config

    config = load_config(config_path)
    console.print(f"[bold]Comparing[/bold] {path_a} vs {path_b}")

    with console.status("[bold cyan]Running comparison..."):
        run_a, run_b, comparisons = asyncio.run(run_comparison(config, path_a, path_b))

    # Summary
    wins = {"a": 0, "b": 0, "tie": 0}
    for c in comparisons:
        wins[c.winner] += 1

    console.print(f"\n[bold green]Comparison complete![/bold green]")
    table = Table(title="A/B Comparison")
    table.add_column("", style="bold")
    table.add_column("Version A", justify="center")
    table.add_column("Version B", justify="center")
    for criterion in config.criteria:
        score_a = run_a.summary.get(criterion, 0)
        score_b = run_b.summary.get(criterion, 0)
        table.add_row(criterion, f"{score_a:.2f}", f"{score_b:.2f}")
    table.add_row("Wins", str(wins["a"]), str(wins["b"]))
    table.add_row("Ties", str(wins["tie"]), str(wins["tie"]))
    console.print(table)

    total_cost = run_a.total_cost_usd + run_b.total_cost_usd
    console.print(f"\n  Total cost: ${total_cost:.4f}")


@main.command()
@click.option("--config", "config_path", required=True, help="Path to eval.yaml")
def validate(config_path: str):
    """Validate config file without running evaluation."""
    from .config import load_config
    from .criteria import get_criteria

    try:
        config = load_config(config_path)
        get_criteria(config.criteria)
        console.print(f"[green]Config is valid![/green]")
        console.print(f"  Data: {config.data_path}")
        console.print(f"  Judges: {len(config.judges)}")
        console.print(f"  Criteria: {', '.join(config.criteria)}")
    except Exception as e:
        console.print(f"[red]Invalid config:[/red] {e}")
        sys.exit(1)


@main.command(name="list-criteria")
def list_criteria():
    """Show all built-in evaluation criteria."""
    from .criteria.builtin import BUILTIN_CRITERIA

    table = Table(title="Built-in Criteria")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    for name, criterion in BUILTIN_CRITERIA.items():
        table.add_row(name, criterion.description[:80] + "...")
    console.print(table)


@main.command(name="list-templates")
def list_templates_cmd():
    """Show available evaluation templates."""
    from .templates import list_templates

    table = Table(title="Evaluation Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Criteria")
    for t in list_templates():
        table.add_row(t.name, t.description, ", ".join(t.criteria_names))
    console.print(table)


if __name__ == "__main__":
    main()
