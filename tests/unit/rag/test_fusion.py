from pf_ft_ai.rag.fusion import reciprocal_rank_fusion


def test_should_favor_items_ranked_highly_in_both_lists() -> None:
    vector_ranking = ["a", "b", "c"]
    keyword_ranking = ["a", "c", "b"]

    scores = reciprocal_rank_fusion(vector_ranking, keyword_ranking)

    assert scores["a"] > scores["b"]
    assert scores["a"] > scores["c"]


def test_should_include_items_that_only_appear_in_one_ranking() -> None:
    scores = reciprocal_rank_fusion(["a", "b"], ["c"])

    assert set(scores) == {"a", "b", "c"}


def test_should_return_empty_for_no_rankings() -> None:
    assert reciprocal_rank_fusion() == {}
