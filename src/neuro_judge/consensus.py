"""Multi-judge consensus aggregation."""

from __future__ import annotations

import statistics
from collections import Counter

from .models import ConsensusMethod, JudgeScore


def aggregate_scores(scores: list[JudgeScore], method: ConsensusMethod = ConsensusMethod.MEAN) -> float:
    """Aggregate multiple judge scores into a single consensus score."""
    if not scores:
        return 0.0

    values = [s.score for s in scores]

    if method == ConsensusMethod.MEAN:
        return round(statistics.mean(values), 2)
    elif method == ConsensusMethod.MEDIAN:
        return round(statistics.median(values), 2)
    elif method == ConsensusMethod.MAJORITY_VOTE:
        counter = Counter(values)
        return float(counter.most_common(1)[0][0])
    else:
        return round(statistics.mean(values), 2)


def compute_agreement(scores: list[JudgeScore]) -> float:
    """Compute inter-judge agreement as percentage of scores within 1 point of each other."""
    if len(scores) < 2:
        return 1.0

    values = [s.score for s in scores]
    pairs = 0
    agreements = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            pairs += 1
            if abs(values[i] - values[j]) <= 1:
                agreements += 1

    return round(agreements / pairs, 3) if pairs > 0 else 1.0
