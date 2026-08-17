from __future__ import annotations

from typing import Protocol

from pf_ft_ai.domain.session.entities import Session


class SessionRepository(Protocol):
    async def create(self, session: Session) -> Session: ...

    async def get(self, session_id: str) -> Session | None: ...

    async def touch(self, session_id: str, *, expected_version: int) -> Session: ...

    async def expire(self, session_id: str, *, expected_version: int) -> Session: ...

    async def terminate(self, session_id: str, *, expected_version: int) -> Session: ...
