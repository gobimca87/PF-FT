from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.domain.session.entities import Session
from pf_ft_ai.domain.session.states import SessionStatus
from pf_ft_ai.domain.versioning import assert_expected_version


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = asyncio.Lock()

    async def create(self, session: Session) -> Session:
        async with self._lock:
            if session.session_id in self._sessions:
                raise WorkflowError(f"Session already exists: {session.session_id}")
            self._sessions[session.session_id] = session
            return session

    async def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def touch(self, session_id: str, *, expected_version: int) -> Session:
        return await self._transition(
            session_id, expected_version=expected_version, status=SessionStatus.ACTIVE
        )

    async def expire(self, session_id: str, *, expected_version: int) -> Session:
        return await self._transition(
            session_id, expected_version=expected_version, status=SessionStatus.EXPIRED
        )

    async def terminate(self, session_id: str, *, expected_version: int) -> Session:
        return await self._transition(
            session_id, expected_version=expected_version, status=SessionStatus.TERMINATED
        )

    async def _transition(
        self, session_id: str, *, expected_version: int, status: SessionStatus
    ) -> Session:
        async with self._lock:
            existing = self._sessions.get(session_id)
            if existing is None:
                raise WorkflowError(f"Session not found: {session_id}")
            assert_expected_version(
                current_version=existing.version, expected_version=expected_version
            )
            updated = existing.model_copy(
                update={
                    "status": status,
                    "version": existing.version + 1,
                    "last_activity_at": datetime.now(UTC),
                }
            )
            self._sessions[session_id] = updated
            return updated
