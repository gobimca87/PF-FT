from datetime import UTC, datetime

from pf_ft_ai.messaging.reliability.dead_letter import DeadLetterRecord, InMemoryDeadLetterStore


def _record(event_id: str = "evt-1") -> DeadLetterRecord:
    now = datetime.now(UTC)
    return DeadLetterRecord(
        event_id=event_id,
        event_type="OFFICIAL_UPDATED",
        event_version="1.0.0",
        source="affiliation-service",
        subscription="pf-ft-ai-runtime-dev",
        first_received_at=now,
        last_attempt_at=now,
        attempt_count=5,
        failure_code="MAX_RETRIES_EXCEEDED",
        failure_reason="downstream timeout",
        correlation_id="corr-1",
        payload={"official_id": "official-123"},
    )


async def test_should_store_and_fetch_a_dead_letter_record() -> None:
    store = InMemoryDeadLetterStore()
    await store.put(_record())

    fetched = await store.get("evt-1")

    assert fetched is not None
    assert fetched.failure_code == "MAX_RETRIES_EXCEEDED"
    assert fetched.payload == {"official_id": "official-123"}


async def test_should_return_none_for_a_missing_record() -> None:
    store = InMemoryDeadLetterStore()

    assert await store.get("missing") is None


async def test_should_list_all_records() -> None:
    store = InMemoryDeadLetterStore()
    await store.put(_record("evt-1"))
    await store.put(_record("evt-2"))

    records = await store.list_all()

    assert {record.event_id for record in records} == {"evt-1", "evt-2"}
