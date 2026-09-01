from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar

RecordT = TypeVar("RecordT")


def deduplicate_records(
    records: Iterable[RecordT], *, key: Callable[[RecordT], str]
) -> list[RecordT]:
    """doc 8 §55 — detect duplicates by the enterprise identifier."""
    seen: set[str] = set()
    deduplicated: list[RecordT] = []
    for record in records:
        record_key = key(record)
        if record_key in seen:
            continue
        seen.add(record_key)
        deduplicated.append(record)
    return deduplicated


@dataclass(frozen=True)
class AggregationResult(Generic[RecordT]):
    records: tuple[RecordT, ...]
    expected_count: int
    received_count: int
    duplicate_count: int
    is_complete: bool


def aggregate_records(
    records: Iterable[RecordT], *, key: Callable[[RecordT], str], expected_count: int
) -> AggregationResult[RecordT]:
    """doc 8 §57 — deterministic: deduplicate, then check completeness (§56)."""
    all_records = list(records)
    deduplicated = deduplicate_records(all_records, key=key)
    return AggregationResult(
        records=tuple(deduplicated),
        expected_count=expected_count,
        received_count=len(deduplicated),
        duplicate_count=len(all_records) - len(deduplicated),
        is_complete=len(deduplicated) == expected_count,
    )
