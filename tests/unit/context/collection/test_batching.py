import pytest

from pf_ft_ai.common.exceptions import ValidationError
from pf_ft_ai.context.collection.batching import BatchRange, split_into_batches


def test_should_split_103_teams_into_6_batches_with_partial_final_batch() -> None:
    """doc 8 §37 worked example."""
    batches = split_into_batches(103, batch_size=20)

    assert len(batches) == 6
    assert [batch.record_count for batch in batches] == [20, 20, 20, 20, 20, 3]
    assert batches[-1] == BatchRange(index=6, start=101, end=103)


def test_should_split_127_officials_into_7_batches_with_partial_final_batch() -> None:
    """doc 8 §38 worked example."""
    batches = split_into_batches(127, batch_size=20)

    assert len(batches) == 7
    assert [batch.record_count for batch in batches] == [20, 20, 20, 20, 20, 20, 7]
    assert batches[-1] == BatchRange(index=7, start=121, end=127)


def test_should_produce_one_batch_for_exactly_20_records() -> None:
    batches = split_into_batches(20, batch_size=20)

    assert batches == [BatchRange(index=1, start=1, end=20)]


def test_should_produce_one_partial_batch_for_fewer_than_batch_size() -> None:
    batches = split_into_batches(5, batch_size=20)

    assert batches == [BatchRange(index=1, start=1, end=5)]


def test_should_produce_empty_batches_for_zero_records() -> None:
    assert split_into_batches(0, batch_size=20) == []


def test_should_produce_empty_batches_for_negative_count() -> None:
    assert split_into_batches(-5, batch_size=20) == []


def test_should_split_exact_multiple_with_no_partial_batch() -> None:
    batches = split_into_batches(40, batch_size=20)

    assert [batch.record_count for batch in batches] == [20, 20]


def test_should_reject_non_positive_batch_size() -> None:
    with pytest.raises(ValidationError, match="batch_size must be greater than zero"):
        split_into_batches(100, batch_size=0)


def test_batch_ranges_should_cover_every_record_without_gaps_or_overlap() -> None:
    batches = split_into_batches(103, batch_size=20)

    covered = [record for batch in batches for record in range(batch.start, batch.end + 1)]
    assert covered == list(range(1, 104))
