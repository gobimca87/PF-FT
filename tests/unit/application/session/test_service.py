from datetime import UTC, datetime, timedelta

import pytest

from pff_fa_ai.application.session.service import SessionService
from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.configuration.models import SessionSettings
from pff_fa_ai.domain.session.entities import Session
from pff_fa_ai.domain.session.states import SessionStatus
from pff_fa_ai.infrastructure.persistence.in_memory_session_repository import (
    InMemorySessionRepository,
)

SETTINGS = SessionSettings(idle_timeout_minutes=30, absolute_timeout_hours=8)


def _service() -> SessionService:
    return SessionService(InMemorySessionRepository(), SETTINGS)


async def test_should_create_a_session_with_absolute_timeout_from_settings() -> None:
    service = _service()

    session = await service.create_session(
        session_id="sess-1", conversation_id="conv-1", user_reference="user-1"
    )

    expected_expiry = session.started_at + timedelta(hours=SETTINGS.absolute_timeout_hours)
    assert session.expires_at == expected_expiry


async def test_should_resolve_an_active_session_by_touching_it() -> None:
    service = _service()
    await service.create_session(
        session_id="sess-1", conversation_id="conv-1", user_reference="user-1"
    )

    resolved = await service.resolve_session("sess-1")

    assert resolved.status is SessionStatus.ACTIVE


async def test_should_raise_when_resolving_an_unknown_session() -> None:
    service = _service()

    with pytest.raises(WorkflowError, match="not found"):
        await service.resolve_session("missing")


async def test_should_expire_a_session_past_absolute_timeout() -> None:
    repository = InMemorySessionRepository()
    service = SessionService(repository, SETTINGS)
    now = datetime.now(UTC)
    stale_session = Session(
        session_id="sess-stale",
        conversation_id="conv-1",
        user_reference="user-1",
        status=SessionStatus.ACTIVE,
        started_at=now - timedelta(hours=9),
        last_activity_at=now - timedelta(hours=9),
        expires_at=now - timedelta(hours=1),
    )
    await repository.create(stale_session)

    resolved = await service.resolve_session("sess-stale")

    assert resolved.status is SessionStatus.EXPIRED


async def test_should_terminate_a_session() -> None:
    service = _service()
    await service.create_session(
        session_id="sess-1", conversation_id="conv-1", user_reference="user-1"
    )

    terminated = await service.terminate_session("sess-1")

    assert terminated.status is SessionStatus.TERMINATED


async def test_should_raise_when_terminating_an_unknown_session() -> None:
    service = _service()

    with pytest.raises(WorkflowError, match="not found"):
        await service.terminate_session("missing")
