from pf_ft_ai.integration.execution.idempotency import (
    InMemoryIdempotencyStore,
    build_idempotency_key,
)
from pf_ft_ai.integration.execution.states import IdempotencyStatus


def test_should_build_key_from_workflow_and_operation_id() -> None:
    key = build_idempotency_key(workflow_instance_id="wf-123", operation_id="submit_application")

    assert key == "wf-123:submit_application"


async def test_should_return_none_for_an_unknown_key() -> None:
    store = InMemoryIdempotencyStore()

    assert await store.get_status("missing") is None


async def test_should_track_the_idempotency_lifecycle() -> None:
    store = InMemoryIdempotencyStore()
    key = build_idempotency_key(workflow_instance_id="wf-1", operation_id="submit")

    await store.mark_in_progress(key)
    assert await store.get_status(key) is IdempotencyStatus.IN_PROGRESS

    await store.mark_completed(key)
    assert await store.get_status(key) is IdempotencyStatus.COMPLETED


async def test_should_track_a_failed_operation() -> None:
    store = InMemoryIdempotencyStore()
    key = build_idempotency_key(workflow_instance_id="wf-1", operation_id="submit")

    await store.mark_in_progress(key)
    await store.mark_failed(key)

    assert await store.get_status(key) is IdempotencyStatus.FAILED
