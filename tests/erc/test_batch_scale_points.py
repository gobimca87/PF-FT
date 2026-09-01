from pff_fa_ai.context.collection.batching import split_into_batches

# doc 22 §52 / DEVELOPMENT-GUIDE Phase 17: ERC batching must be explicitly verified at
# these named scale points, in addition to the general-purpose edge cases already
# covered by tests/unit/context/collection/test_batching.py. The agreed batch size
# (config/base/batching.yaml `batching.batch_size`) is 20.
_BATCH_SIZE = 20


def test_should_process_a_single_entity_without_loss() -> None:
    batches = split_into_batches(1, batch_size=_BATCH_SIZE)

    assert len(batches) == 1
    assert batches[0].record_count == 1
    assert batches[0].start == 1
    assert batches[0].end == 1


def test_should_process_exactly_20_entities_in_a_single_full_batch() -> None:
    batches = split_into_batches(20, batch_size=_BATCH_SIZE)

    assert len(batches) == 1
    assert batches[0].record_count == 20


def test_should_process_21_entities_as_one_full_batch_plus_one() -> None:
    """The one-over-boundary case: 20 fills batch 1 exactly, entity 21 forces batch 2."""
    batches = split_into_batches(21, batch_size=_BATCH_SIZE)

    assert len(batches) == 2
    assert [batch.record_count for batch in batches] == [20, 1]


def test_should_process_40_entities_as_two_exact_full_batches() -> None:
    batches = split_into_batches(40, batch_size=_BATCH_SIZE)

    assert len(batches) == 2
    assert [batch.record_count for batch in batches] == [20, 20]


def test_should_process_exactly_100_entities_as_five_full_batches() -> None:
    batches = split_into_batches(100, batch_size=_BATCH_SIZE)

    assert len(batches) == 5
    assert [batch.record_count for batch in batches] == [20, 20, 20, 20, 20]


def test_should_process_100_plus_entities_without_data_loss() -> None:
    """doc 22 §53: retrieved count must equal aggregated count for N entities."""
    total = 137
    batches = split_into_batches(total, batch_size=_BATCH_SIZE)

    covered = sum(batch.record_count for batch in batches)
    assert covered == total
    assert len(batches) == 7
    assert batches[-1].record_count == 17
