from pf_ft_ai.context.collection.aggregator import aggregate_records, deduplicate_records


def test_should_deduplicate_by_enterprise_identifier() -> None:
    records = [{"id": "team-a"}, {"id": "team-b"}, {"id": "team-a"}]

    deduplicated = deduplicate_records(records, key=lambda record: record["id"])

    assert deduplicated == [{"id": "team-a"}, {"id": "team-b"}]


def test_should_preserve_first_occurrence_order() -> None:
    records = [{"id": "c"}, {"id": "a"}, {"id": "b"}, {"id": "a"}]

    deduplicated = deduplicate_records(records, key=lambda record: record["id"])

    assert [record["id"] for record in deduplicated] == ["c", "a", "b"]


def test_should_mark_aggregation_complete_when_counts_match() -> None:
    records = [{"id": "1"}, {"id": "2"}, {"id": "3"}]

    result = aggregate_records(records, key=lambda record: record["id"], expected_count=3)

    assert result.is_complete is True
    assert result.received_count == 3
    assert result.duplicate_count == 0


def test_should_mark_aggregation_incomplete_when_records_are_missing() -> None:
    """doc 8 §56: expected 100, only 95 received -> incomplete."""
    records = [{"id": str(i)} for i in range(95)]

    result = aggregate_records(records, key=lambda record: record["id"], expected_count=100)

    assert result.is_complete is False
    assert result.received_count == 95


def test_should_count_duplicates_removed_during_aggregation() -> None:
    records = [{"id": "a"}, {"id": "a"}, {"id": "b"}]

    result = aggregate_records(records, key=lambda record: record["id"], expected_count=2)

    assert result.duplicate_count == 1
    assert result.received_count == 2
    assert result.is_complete is True
