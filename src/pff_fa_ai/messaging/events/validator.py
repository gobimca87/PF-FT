from __future__ import annotations

from collections.abc import Iterable

from pff_fa_ai.common.exceptions import ValidationError
from pff_fa_ai.messaging.events.models import EventEnvelope


def validate_envelope(envelope: EventEnvelope, *, known_sources: Iterable[str]) -> None:
    """doc 11 §36/§122 — structural field presence is enforced by `EventEnvelope` itself
    (Pydantic required fields); this covers the checks that need actual logic."""
    known = frozenset(known_sources)
    if envelope.source not in known:
        raise ValidationError(
            f"Unknown or unapproved event source: {envelope.source}",
            details={"source": envelope.source, "event_id": envelope.event_id},
        )
    if envelope.published_at < envelope.occurred_at:
        raise ValidationError(
            "Event published_at precedes occurred_at — malformed timestamps",
            details={
                "event_id": envelope.event_id,
                "occurred_at": envelope.occurred_at.isoformat(),
                "published_at": envelope.published_at.isoformat(),
            },
        )
