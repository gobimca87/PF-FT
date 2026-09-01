from __future__ import annotations

from collections.abc import Sequence

_DEFAULT_K = 60


def reciprocal_rank_fusion(*rankings: Sequence[str], k: int = _DEFAULT_K) -> dict[str, float]:
    """Doc 13 §64 candidate fusion — combines vector and keyword rankings by rank, not
    by raw score, so incompatible score scales never distort the fused order."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return scores
