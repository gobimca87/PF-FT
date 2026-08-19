"""doc 22 §72/§79 "Performance Baseline" / "ERC Performance Testing": establishes a
wall-clock regression guard for ERC batching + aggregation at large entity counts, so an
accidental O(n^2) change (e.g. swapping the dedup set for a list-based membership check)
gets caught here rather than in a live environment. The bound is deliberately generous —
this is a regression guard, not a precise latency SLA (no production benchmark exists
yet to calibrate a tighter one)."""

import time

from pf_ft_ai.context.collection.aggregator import aggregate_records
from pf_ft_ai.context.collection.batching import split_into_batches
from tests.fixtures.factories import make_enterprise_records

_LARGE_SCALE_BOUND_SECONDS = 1.0


def test_batching_5000_entities_should_complete_within_the_performance_baseline() -> None:
    started = time.perf_counter()

    batches = split_into_batches(5000, batch_size=20)

    elapsed = time.perf_counter() - started
    assert len(batches) == 250
    assert elapsed < _LARGE_SCALE_BOUND_SECONDS


def test_aggregating_5000_entities_with_duplicates_should_complete_within_the_baseline() -> None:
    records = make_enterprise_records(5000, entity_type="official")
    duplicated = records + records[:500]  # simulate a 10% duplicate-delivery rate

    started = time.perf_counter()
    result = aggregate_records(duplicated, key=lambda record: record["id"], expected_count=5000)
    elapsed = time.perf_counter() - started

    assert result.is_complete is True
    assert result.duplicate_count == 500
    assert elapsed < _LARGE_SCALE_BOUND_SECONDS
