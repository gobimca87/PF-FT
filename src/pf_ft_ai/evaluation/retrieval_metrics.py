from __future__ import annotations

import math
from collections.abc import Sequence, Set

# doc 21 §38 names these metrics without prescribing formulas — standard information
# retrieval definitions, evaluated per-query. `retrieved` is a ranked list of IDs (most
# relevant first); `relevant` is the ground-truth relevant ID set from the golden case.


def recall_at_k(retrieved: Sequence[str], relevant: Set[str], *, k: int) -> float:
    if not relevant:
        return 0.0
    hits = len(set(retrieved[:k]) & relevant)
    return hits / len(relevant)


def precision_at_k(retrieved: Sequence[str], relevant: Set[str], *, k: int) -> float:
    if k <= 0:
        return 0.0
    hits = len(set(retrieved[:k]) & relevant)
    return hits / k


def hit_rate_at_k(retrieved: Sequence[str], relevant: Set[str], *, k: int) -> float:
    return 1.0 if set(retrieved[:k]) & relevant else 0.0


def reciprocal_rank(retrieved: Sequence[str], relevant: Set[str]) -> float:
    for rank, item_id in enumerate(retrieved, start=1):
        if item_id in relevant:
            return 1.0 / rank
    return 0.0


def mean_reciprocal_rank(per_query_ranks: Sequence[float]) -> float:
    if not per_query_ranks:
        return 0.0
    return sum(per_query_ranks) / len(per_query_ranks)


def ndcg_at_k(retrieved: Sequence[str], relevant: Set[str], *, k: int) -> float:
    """Binary relevance NDCG@K — golden cases mark an item relevant or not, no graded scale."""
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, item_id in enumerate(retrieved[:k], start=1)
        if item_id in relevant
    )
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    if idcg == 0:
        return 0.0
    return dcg / idcg
