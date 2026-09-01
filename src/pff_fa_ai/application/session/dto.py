from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.domain.session.entities import Session
from pff_fa_ai.domain.session.states import SessionStatus


class SessionView(BaseModel):
    model_config = ConfigDict(frozen=True)

    session_id: str
    conversation_id: str
    status: SessionStatus
    started_at: datetime
    last_activity_at: datetime
    expires_at: datetime

    @classmethod
    def from_session(cls, session: Session) -> SessionView:
        return cls(
            session_id=session.session_id,
            conversation_id=session.conversation_id,
            status=session.status,
            started_at=session.started_at,
            last_activity_at=session.last_activity_at,
            expires_at=session.expires_at,
        )
