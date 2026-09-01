from datetime import UTC, datetime, timedelta

import pytest

from pff_fa_ai.common.exceptions import ValidationError
from pff_fa_ai.messaging.events.models import EventEnvelope
from pff_fa_ai.messaging.events.validator import validate_envelope


def _envelope(**overrides: object) -> EventEnvelope:
    now = datetime.now(UTC)
    defaults: dict[str, object] = {
        "event_id": "evt-123",
        "event_type": "HIL_TASK_COMPLETED",
        "event_version": "1.0.0",
        "source": "affiliation-service",
        "subject": "official/official-123",
        "occurred_at": now,
        "published_at": now,
        "correlation_id": "corr-123",
        "tenant_id": "tenant-1",
        "organization_id": "club-123",
    }
    defaults.update(overrides)
    return EventEnvelope(**defaults)  # type: ignore[arg-type]


def test_should_accept_an_event_from_a_known_source() -> None:
    validate_envelope(_envelope(), known_sources=frozenset({"affiliation-service"}))


def test_should_reject_an_unknown_source() -> None:
    with pytest.raises(ValidationError, match="Unknown or unapproved event source"):
        validate_envelope(
            _envelope(source="rogue-service"), known_sources=frozenset({"affiliation-service"})
        )


def test_should_reject_published_at_before_occurred_at() -> None:
    now = datetime.now(UTC)
    envelope = _envelope(occurred_at=now, published_at=now - timedelta(seconds=5))

    with pytest.raises(ValidationError, match="precedes occurred_at"):
        validate_envelope(envelope, known_sources=frozenset({"affiliation-service"}))
