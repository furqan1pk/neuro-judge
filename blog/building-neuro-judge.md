# What I Learned Evaluating 4 Production GenAI Pipelines

*Building neuro-judge: an open-source LLM-as-a-Judge framework*

## The Problem

Every team shipping LLM features faces the same question: "Is our output actually good?"

At Wayfair, I built evaluation frameworks for 4 production GenAI pipelines — product tag validation, image evaluation, duplicate detection, and customer review analysis. The hardest part wasn't building the pipelines. It was knowing whether they worked.

Manual review doesn't scale. Traditional metrics (BLEU, ROUGE) don't capture what matters for generative outputs. You need something that understands context, nuance, and intent.

That's where LLM-as-a-Judge (LLMaaJ) comes in.

## What is LLM-as-a-Judge?

The idea is simple: use one LLM to evaluate another LLM's outputs. Like having a senior reviewer grade homework, except the reviewer is also an AI — one you've carefully prompted with scoring rubrics.

It sounds circular, but it works remarkably well when done right:
- Correlates highly with human judgment (we validated this across our pipelines)
- Scales to thousands of samples
- Costs pennies per evaluation
- Provides reasoning, not just scores

## What I Built

**neuro-judge** packages everything I learned into a pip-installable tool:

```bash
pip install neuro-judge
neuro-judge init
neuro-judge run --config eval.yaml
```

### Key design decisions:

**1. Multi-judge consensus** — A single judge can be biased. Running 2-3 judges and averaging catches systematic blind spots. At Wayfair, we found that Claude and GPT-4o disagreed most on edge cases — exactly where you want multiple perspectives.

**2. Cost tracking built in** — Every evaluation call costs money. When you're running evals across 4 pipelines daily, costs add up fast. neuro-judge tracks every token and gives you cost-per-criterion breakdowns.

**3. Structured prompts with mandatory JSON** — The biggest failure mode is unparseable judge responses. Markdown fences wrapping JSON, extra commentary, partial responses. We handle all of it with defensive parsing.

**4. Template-based criteria** — Most teams evaluate the same things (accuracy, relevance, safety). Pre-built templates let you start in 60 seconds instead of writing prompts from scratch.

## Results

[TODO: Add screenshots of HTML report]
[TODO: Add benchmark numbers comparing judge scores to human scores]

## Try It

```bash
pip install neuro-judge
neuro-judge init
# Set ANTHROPIC_API_KEY in .env
neuro-judge run --config eval.yaml
```

The HTML report opens with radar charts, score distributions, and drill-down reasoning for every sample.

## What I Learned

1. **Temperature 0 matters** — Deterministic judge scores are reproducible. Set temperature to 0 for eval, always.
2. **Multi-judge > single judge** — Even a 2-judge mean is significantly more reliable.
3. **Cost per eval is the real constraint** — Not accuracy, not speed. Teams stop evaluating when it gets expensive.
4. **Criteria design is the hard part** — The framework is easy. Defining what "good" means for your specific use case takes iteration.

---

*Furqan Arshad is an ML Scientist II at Wayfair, where he builds GenAI systems and evaluation frameworks. Previously at UC Davis (neural decoding) and Meta Innovation Lab (health ML).*
