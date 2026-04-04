# neuro-judge

**LLM-as-a-Judge evaluation framework.** Multi-model, multi-criteria, with cost tracking and beautiful HTML reports.

Built from production experience evaluating 4 GenAI pipelines at scale.

```bash
pip install neuro-judge
```

## Quick Start (60 seconds)

```bash
# 1. Initialize project with sample data
neuro-judge init

# 2. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run evaluation
neuro-judge run --config eval.yaml
```

Opens an HTML report with radar charts, score distributions, cost breakdown, and detailed judge reasoning.

## One-Liner Python API

```python
from neuro_judge import quick_eval

results = quick_eval(
    data="outputs.jsonl",
    criteria=["accuracy", "relevance"],
    judge="claude-sonnet-4-6",
)
print(results.summary)  # {'accuracy': 4.2, 'relevance': 4.5}
```

## Full Python API

```python
from neuro_judge import Evaluator

evaluator = Evaluator(
    judges=["claude-sonnet-4-6", "gpt-4o"],
    criteria=["accuracy", "relevance", "coherence"],
    consensus="mean",
)
run = evaluator.run(data="outputs.jsonl")
run.to_html("report.html")
```

## Data Format

Your JSONL file — one line per sample:

```jsonl
{"input": "What is the return policy?", "output": "30 day returns.", "reference": "30-day return policy, full refund on unused items."}
{"input": "Describe this product", "output": "Blue velvet sofa", "image_url": "https://...jpg"}
```

| Field | Required | Description |
|-------|----------|-------------|
| `input` | Yes | The prompt/question sent to your LLM |
| `output` | Yes | Your LLM's response to evaluate |
| `reference` | No | Ground truth / expected answer |
| `image_url` | No | Image URL for multimodal evaluation |
| `id` | No | Sample identifier (auto-generated if missing) |

## CLI Commands

| Command | Description |
|---------|-------------|
| `neuro-judge init [--template rag]` | Scaffold config + sample data |
| `neuro-judge run --config eval.yaml` | Run full evaluation pipeline |
| `neuro-judge compare --a v1.jsonl --b v2.jsonl --config eval.yaml` | A/B comparison of two versions |
| `neuro-judge validate --config eval.yaml` | Validate config without running |
| `neuro-judge list-criteria` | Show built-in criteria |
| `neuro-judge list-templates` | Show evaluation templates |

## Evaluation Templates

Pre-built configurations for common use cases:

| Template | Criteria | Use Case |
|----------|----------|----------|
| `general` | accuracy, relevance, coherence | Default quality check |
| `rag-accuracy` | faithfulness, relevance, completeness | RAG pipeline evaluation |
| `summarization` | completeness, conciseness, faithfulness | Summary quality |
| `safety` | safety, helpfulness | Toxicity & safety checks |

```bash
neuro-judge init --template rag-accuracy
```

## Supported Providers

| Provider | Models | Multimodal |
|----------|--------|------------|
| Anthropic | Claude Sonnet, Haiku, Opus | Yes |
| OpenAI | GPT-4o, GPT-4o-mini | Yes |
| Google | Gemini 2.0 Flash, 2.5 Pro | Yes |
| Ollama | Any local model | With vision models |

## A/B Comparison

Compare two prompt versions head-to-head:

```bash
neuro-judge compare \
  --a outputs_v1.jsonl \
  --b outputs_v2.jsonl \
  --config eval.yaml
```

Produces win/loss/tie counts and per-criterion score comparison.

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run LLM Evaluation
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    pip install neuro-judge
    neuro-judge run --config eval.yaml
```

See `.github/workflows/eval.yml` for a full example that posts results as PR comments.

## Configuration

```yaml
data_path: outputs.jsonl
judges:
  - provider: anthropic
    model: claude-sonnet-4-6
    temperature: 0.0
  - provider: openai
    model: gpt-4o
criteria:
  - accuracy
  - relevance
  - coherence
consensus: mean          # mean, median, or majority_vote
concurrency: 5
output_dir: ./reports
multimodal: false        # set true for image evaluation
```

## How It Works

1. **Load** your LLM outputs from JSONL
2. **Judge** each output using LLM-as-a-Judge (one LLM evaluates another's outputs)
3. **Consensus** across multiple judges (mean, median, or majority vote)
4. **Report** with scores, reasoning, cost tracking, and visualizations

## Built With

- Python 3.10+
- Pydantic v2 for data models
- Click for CLI
- Chart.js for report visualizations
- Async execution for parallel judge calls

## License

MIT

## Author

**Furqan Arshad** — ML Scientist II at Wayfair, building GenAI evaluation systems at scale.

- [Portfolio](https://furqan1pk.github.io)
- [LinkedIn](https://linkedin.com/in/furqaanarshad)
- [GitHub](https://github.com/furqan1pk)
