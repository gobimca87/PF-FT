import asyncio

from pff_fa_ai.integration.execution.states import IdempotencyStatus
from pff_fa_ai.messaging.reliability.idempotency import (
    InMemoryEventIdempotencyStore,
    build_event_idempotency_key,
)


def test_build_key_should_combine_event_id_and_consumer_id() -> None:
    assert (
        build_event_idempotency_key(event_id="evt-1", consumer_id="ai-workflow")
        == "evt-1:ai-workflow"
    )


async def test_should_claim_a_fresh_key() -> None:
    store = InMemoryEventIdempotencyStore()

    claimed = await store.try_claim("evt-1:ai-workflow")

    assert claimed is True
    assert await store.get_status("evt-1:ai-workflow") is IdempotencyStatus.IN_PROGRESS


async def test_should_reject_claiming_an_in_progress_key() -> None:
    store = InMemoryEventIdempotencyStore()
    await store.try_claim("evt-1:ai-workflow")

    claimed_again = await store.try_claim("evt-1:ai-workflow")

    assert claimed_again is False


async def test_should_reject_claiming_a_completed_key() -> None:
    store = InMemoryEventIdempotencyStore()
    key = "evt-1:ai-workflow"
    await store.try_claim(key)
    await store.mark_completed(key)

    assert await store.try_claim(key) is False


async def test_should_allow_reclaiming_a_failed_key() -> None:
    store = InMemoryEventIdempotencyStore()
    key = "evt-1:ai-workflow"
    await store.try_claim(key)
    await store.mark_failed(key)

    assert await store.try_claim(key) is True


async def test_concurrent_claims_should_only_let_one_succeed() -> None:
    store = InMemoryEventIdempotencyStore()
    key = "evt-1:ai-workflow"

    results = await asyncio.gather(*(store.try_claim(key) for _ in range(20)))

    assert results.count(True) == 1
