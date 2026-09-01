from datetime import UTC, datetime

from pff_fa_ai.messaging.events.models import EventEnvelope


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


def test_should_construct_a_minimal_valid_envelope() -> None:
    envelope = _envelope()

    assert envelope.event_id == "evt-123"
    assert envelope.payload == {}
    assert envelope.causation_id is None
    assert envelope.workflow_instance_id is None


def test_should_carry_a_workflow_instance_id_when_supplied() -> None:
    envelope = _envelope(workflow_instance_id="wf-123")

    assert envelope.workflow_instance_id == "wf-123"


def test_should_carry_the_payload() -> None:
    envelope = _envelope(payload={"official_id": "official-123"})

    assert envelope.payload == {"official_id": "official-123"}
