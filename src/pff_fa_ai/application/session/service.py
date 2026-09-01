from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.configuration.models import SessionSettings
from pff_fa_ai.domain.session.entities import Session
from pff_fa_ai.domain.session.repository import SessionRepository
from pff_fa_ai.domain.session.states import SessionStatus


class SessionService:
    def __init__(self, repository: SessionRepository, settings: SessionSettings) -> None:
        self._repository = repository
        self._settings = settings

    async def create_session(
        self, *, session_id: str, conversation_id: str, user_reference: str
    ) -> Session:
        now = datetime.now(UTC)
        session = Session(
            session_id=session_id,
            conversation_id=conversation_id,
            user_reference=user_reference,
            status=SessionStatus.CREATED,
            started_at=now,
            last_activity_at=now,
            expires_at=now + timedelta(hours=self._settings.absolute_timeout_hours),
        )
        return await self._repository.create(session)

    async def resolve_session(self, session_id: str) -> Session:
        session = await self._repository.get(session_id)
        if session is None:
            raise WorkflowError(f"Session not found: {session_id}")
        if self._is_expired(session):
            return await self._repository.expire(session_id, expected_version=session.version)
        return await self._repository.touch(session_id, expected_version=session.version)

    async def terminate_session(self, session_id: str) -> Session:
        session = await self._repository.get(session_id)
        if session is None:
            raise WorkflowError(f"Session not found: {session_id}")
        return await self._repository.terminate(session_id, expected_version=session.version)

    def _is_expired(self, session: Session) -> bool:
        now = datetime.now(UTC)
        if now >= session.expires_at:
            return True
        idle_for = now - session.last_activity_at
        return idle_for >= timedelta(minutes=self._settings.idle_timeout_minutes)
