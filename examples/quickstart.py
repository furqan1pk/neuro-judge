"""Quick start example for neuro-judge."""

from neuro_judge import quick_eval

# One-liner evaluation
results = quick_eval(
    data="sample_data.jsonl",
    criteria=["accuracy", "relevance", "coherence"],
    judge="claude-sonnet-4-6",
)

# Print summary
for criterion, score in results.summary.items():
    print(f"  {criterion}: {score:.2f} / 5.00")

print(f"\nTotal cost: ${results.total_cost_usd:.4f}")
print(f"Total time: {results.total_time_seconds:.1f}s")
