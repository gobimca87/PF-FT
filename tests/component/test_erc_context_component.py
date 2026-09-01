"""doc 22 §14 "Component Testing" — exercises the ERC context component as a whole
(batching → collection → aggregation working together), rather than each function in
isolation the way `tests/unit/context/collection/` already does."""

from pff_fa_ai.context.collection.aggregator import aggregate_records
from pff_fa_ai.context.collection.batching import split_into_batches
from tests.fixtures.factories import make_enterprise_records

_BATCH_SIZE = 20


def _collect_in_batches(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Simulates the collection component: split into batches, then "retrieve" each
    batch (here, a direct slice — a real collector would call the enterprise API per
    batch) and flatten the results back into a single record stream for aggregation."""
    batches = split_into_batches(len(records), batch_size=_BATCH_SIZE)
    collected: list[dict[str, str]] = []
    for batch in batches:
        collected.extend(records[batch.start - 1 : batch.end])
    return collected


def test_should_batch_collect_and_aggregate_100_plus_teams_without_loss() -> None:
    records = make_enterprise_records(137, entity_type="team")

    collected = _collect_in_batches(records)
    result = aggregate_records(collected, key=lambda record: record["id"], expected_count=137)

    assert result.is_complete is True
    assert result.received_count == 137
    assert result.duplicate_count == 0
    assert {record["id"] for record in result.records} == {record["id"] for record in records}


def test_should_report_incomplete_when_a_batch_is_dropped_mid_collection() -> None:
    """Simulates a partial-batch collection failure (doc 8 §55-57 completeness check)."""
    records = make_enterprise_records(45, entity_type="official")
    collected = _collect_in_batches(records)
    dropped = [record for record in collected if not record["id"].endswith("-30")]

    result = aggregate_records(dropped, key=lambda record: record["id"], expected_count=45)

    assert result.is_complete is False
    assert result.received_count == 44
    assert result.expected_count == 45


def test_should_deduplicate_records_returned_by_overlapping_batches() -> None:
    records = make_enterprise_records(25, entity_type="course")
    duplicated = records + [records[0], records[5]]  # simulate a retry re-delivering records

    result = aggregate_records(duplicated, key=lambda record: record["id"], expected_count=25)

    assert result.is_complete is True
    assert result.duplicate_count == 2
    assert result.received_count == 25
