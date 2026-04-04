"""Judge prompt construction and response parsing."""

from __future__ import annotations

import json
import re

from .models import Criterion, EvalSample, JudgeScore, LLMResponse
from .providers.base import BaseProvider

SYSTEM_PROMPT = """You are a rigorous AI evaluation judge. Your task is to score an AI system's output on a specific criterion.

You MUST respond with ONLY valid JSON in this exact format:
{"score": <integer>, "reasoning": "<brief explanation>"}

Rules:
- Score must be an integer within the specified scale
- Reasoning must be 1-3 sentences explaining your score
- Be objective and consistent
- If a reference answer is provided, compare the output against it
- Do NOT include any text outside the JSON object"""


def build_judge_prompt(sample: EvalSample, criterion: Criterion) -> str:
    """Construct the evaluation prompt for a single sample + criterion."""
    parts = [
        f"## Evaluation Criterion: {criterion.name}",
        f"{criterion.description}",
        f"Score scale: {criterion.scale_min} (worst) to {criterion.scale_max} (best)",
        "",
        f"## Input",
        f"{sample.input}",
        "",
        f"## Output to Evaluate",
        f"{sample.output}",
    ]

    if sample.reference:
        parts.extend(["", f"## Reference Answer", f"{sample.reference}"])

    if sample.image_url:
        parts.extend(["", "## Note: An image has been provided for visual context. Use it to verify the output."])

    parts.extend(["", "Respond with JSON only:"])
    return "\n".join(parts)


def parse_judge_response(response: LLMResponse, sample_id: str, criterion: str) -> tuple[int, str]:
    """Parse the judge's JSON response, handling markdown fences."""
    text = response.text.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)

    # Try to extract JSON object
    json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    try:
        data = json.loads(text)
        score = int(data.get("score", 3))
        reasoning = str(data.get("reasoning", "No reasoning provided"))
        return score, reasoning
    except (json.JSONDecodeError, ValueError):
        return 3, f"Failed to parse judge response: {response.text[:200]}"


async def run_judge(
    provider: BaseProvider,
    sample: EvalSample,
    criterion: Criterion,
) -> JudgeScore:
    """Run a single judge evaluation."""
    prompt = build_judge_prompt(sample, criterion)
    response = await provider.complete(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        image_url=sample.image_url,
    )
    score, reasoning = parse_judge_response(response, sample.id, criterion.name)
    cost = provider.estimate_cost(response.input_tokens, response.output_tokens)

    return JudgeScore(
        sample_id=sample.id,
        criterion=criterion.name,
        judge_model=response.model,
        judge_provider=response.provider,
        score=score,
        reasoning=reasoning,
        latency_ms=response.latency_ms,
        cost_usd=cost,
    )
