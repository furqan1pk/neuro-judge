# Changelog

All notable changes to `neuro-judge` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-04-04

### Added
- Initial public release.
- Multi-judge consensus (mean / median / min / weighted).
- Real-time cost tracking per criterion / per judge / per sample.
- Self-contained HTML reports with radar charts, score distributions, and judge reasoning.
- Multimodal support (image inputs) for Claude, GPT-4o, Gemini.
- CLI: `neuro-judge init / run / compare / validate / list-criteria / list-templates`.
- Python API: `quick_eval` one-liner and full `Evaluator` class.
- Pre-built evaluation templates (general, rag-accuracy, summarization, safety).
- Async execution with configurable concurrency.

### Roadmap
- Pairwise preference scoring (instead of absolute scores per criterion).
- Human-in-the-loop correction workflow.
- Eval-of-evals: built-in command to detect judge drift over time.
