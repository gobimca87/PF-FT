from __future__ import annotations

from datetime import datetime

from pff_fa_ai.domain.session.states import SessionStatus
from pff_fa_ai.domain.versioning import Versioned


class Session(Versioned):
    session_id: str
    conversation_id: str
    user_reference: str
    status: SessionStatus
    started_at: datetime
    last_activity_at: datetime
    expires_at: datetime
