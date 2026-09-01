from datetime import UTC, datetime, timedelta

import pytest

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.domain.session.entities import Session
from pff_fa_ai.domain.session.states import SessionStatus
from pff_fa_ai.infrastructure.persistence.in_memory_session_repository import (
    InMemorySessionRepository,
)


def _new_session(session_id: str = "sess-1") -> Session:
    now = datetime.now(UTC)
    return Session(
        session_id=session_id,
        conversation_id="conv-1",
        user_reference="user-1",
        status=SessionStatus.CREATED,
        started_at=now,
        last_activity_at=now,
        expires_at=now + timedelta(hours=8),
    )


async def test_should_create_and_get_a_session() -> None:
    repository = InMemorySessionRepository()
    session = _new_session()

    await repository.create(session)

    assert await repository.get(session.session_id) == session


async def test_should_reject_creating_a_duplicate_session_id() -> None:
    repository = InMemorySessionRepository()
    session = _new_session()
    await repository.create(session)

    with pytest.raises(WorkflowError, match="already exists"):
        await repository.create(session)


async def test_should_touch_a_session_and_bump_version() -> None:
    repository = InMemorySessionRepository()
    session = _new_session()
    await repository.create(session)

    touched = await repository.touch(session.session_id, expected_version=1)

    assert touched.status is SessionStatus.ACTIVE
    assert touched.version == 2
    assert touched.last_activity_at >= session.last_activity_at


async def test_should_expire_a_session() -> None:
    repository = InMemorySessionRepository()
    session = _new_session()
    await repository.create(session)

    expired = await repository.expire(session.session_id, expected_version=1)

    assert expired.status is SessionStatus.EXPIRED


async def test_should_terminate_a_session() -> None:
    repository = InMemorySessionRepository()
    session = _new_session()
    await repository.create(session)

    terminated = await repository.terminate(session.session_id, expected_version=1)

    assert terminated.status is SessionStatus.TERMINATED


async def test_should_reject_transition_of_missing_session() -> None:
    repository = InMemorySessionRepository()

    with pytest.raises(WorkflowError, match="not found"):
        await repository.touch("missing", expected_version=1)


async def test_should_reject_transition_with_stale_expected_version() -> None:
    repository = InMemorySessionRepository()
    session = _new_session()
    await repository.create(session)

    with pytest.raises(WorkflowError, match="Concurrency conflict"):
        await repository.touch(session.session_id, expected_version=99)
