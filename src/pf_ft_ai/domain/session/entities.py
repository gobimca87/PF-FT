from __future__ import annotations

from datetime import datetime

from pf_ft_ai.domain.session.states import SessionStatus
from pf_ft_ai.domain.versioning import Versioned


class Session(Versioned):
    session_id: str
    conversation_id: str
    user_reference: str
    status: SessionStatus
    started_at: datetime
    last_activity_at: datetime
    expires_at: datetime
