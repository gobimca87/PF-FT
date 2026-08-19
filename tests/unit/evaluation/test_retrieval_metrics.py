import pytest

from pf_ft_ai.evaluation.retrieval_metrics import (
    hit_rate_at_k,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_k_should_find_all_relevant_items() -> None:
    assert recall_at_k(["a", "b", "c"], {"a", "b"}, k=3) == 1.0


def test_recall_at_k_should_find_partial_relevant_items() -> None:
    assert recall_at_k(["a", "x", "y"], {"a", "b"}, k=3) == 0.5


def test_recall_at_k_should_respect_k() -> None:
    assert recall_at_k(["x", "y", "a"], {"a"}, k=2) == 0.0


def test_recall_at_k_should_return_zero_for_no_relevant_items() -> None:
    assert recall_at_k(["a", "b"], set(), k=2) == 0.0


def test_precision_at_k_should_return_zero_for_a_non_positive_k() -> None:
    assert precision_at_k(["a", "b"], {"a"}, k=0) == 0.0


def test_precision_at_k() -> None:
    assert precision_at_k(["a", "x", "y"], {"a", "b"}, k=3) == pytest.approx(1 / 3)


def test_precision_at_k_perfect() -> None:
    assert precision_at_k(["a", "b"], {"a", "b"}, k=2) == 1.0


def test_hit_rate_at_k_hit() -> None:
    assert hit_rate_at_k(["x", "a"], {"a"}, k=2) == 1.0


def test_hit_rate_at_k_miss() -> None:
    assert hit_rate_at_k(["x", "y"], {"a"}, k=2) == 0.0


def test_reciprocal_rank_first_position() -> None:
    assert reciprocal_rank(["a", "b"], {"a"}) == 1.0


def test_reciprocal_rank_second_position() -> None:
    assert reciprocal_rank(["x", "a"], {"a"}) == 0.5


def test_reciprocal_rank_no_match() -> None:
    assert reciprocal_rank(["x", "y"], {"a"}) == 0.0


def test_mean_reciprocal_rank() -> None:
    assert mean_reciprocal_rank([1.0, 0.5, 0.0]) == pytest.approx(0.5)


def test_mean_reciprocal_rank_empty() -> None:
    assert mean_reciprocal_rank([]) == 0.0


def test_ndcg_at_k_perfect_ranking() -> None:
    assert ndcg_at_k(["a", "b"], {"a", "b"}, k=2) == pytest.approx(1.0)


def test_ndcg_at_k_worse_ranking_scores_lower() -> None:
    perfect = ndcg_at_k(["a", "b"], {"a", "b"}, k=2)
    worse = ndcg_at_k(["x", "a"], {"a", "b"}, k=2)
    assert worse < perfect


def test_ndcg_at_k_no_relevant_items_returns_zero() -> None:
    assert ndcg_at_k(["a", "b"], set(), k=2) == 0.0
