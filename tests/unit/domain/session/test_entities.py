from datetime import UTC, datetime, timedelta

from pf_ft_ai.domain.session.entities import Session
from pf_ft_ai.domain.session.states import SessionStatus


def test_should_create_a_new_session_at_version_one() -> None:
    now = datetime.now(UTC)

    session = Session(
        session_id="sess-123",
        conversation_id="conv-123",
        user_reference="user-123",
        status=SessionStatus.CREATED,
        started_at=now,
        last_activity_at=now,
        expires_at=now + timedelta(minutes=30),
    )

    assert session.version == 1
    assert session.status is SessionStatus.CREATED
    assert session.expires_at > session.started_at
