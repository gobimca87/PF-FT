from datetime import UTC, datetime, timedelta

from pff_fa_ai.context.erc.models import (
    Erc,
    ErcCompleteness,
    ErcSection,
    ErcValidationResult,
    compute_freshness,
)
from pff_fa_ai.context.erc.states import (
    ErcLifecycleStatus,
    ErcSectionStatus,
    ErcValidationStatus,
    FreshnessStatus,
)


def test_should_compute_fresh_status_before_ttl_expires() -> None:
    now = datetime.now(UTC)
    freshness = compute_freshness(
        retrieved_at=now, ttl_seconds=300, now=now + timedelta(seconds=10)
    )

    assert freshness.status is FreshnessStatus.FRESH


def test_should_compute_expired_status_after_ttl_elapses() -> None:
    now = datetime.now(UTC)
    freshness = compute_freshness(
        retrieved_at=now, ttl_seconds=300, now=now + timedelta(seconds=301)
    )

    assert freshness.status is FreshnessStatus.EXPIRED


def test_should_create_an_erc_section_with_default_version() -> None:
    section = ErcSection(name="teams", status=ErcSectionStatus.COMPLETE)

    assert section.section_version == 1
    assert section.data == {}


def test_should_track_erc_completeness() -> None:
    completeness = ErcCompleteness(
        required_sections=6, completed_sections=5, missing_sections=("officials",)
    )

    assert completeness.missing_sections == ("officials",)


def test_should_create_a_validation_result() -> None:
    result = ErcValidationResult(status=ErcValidationStatus.VALID, checked_at=datetime.now(UTC))

    assert result.errors == ()
    assert result.warnings == ()


def test_should_create_a_new_erc_at_version_one() -> None:
    now = datetime.now(UTC)
    erc = Erc(
        erc_id="erc-123",
        schema_version="1.0.0",
        status=ErcLifecycleStatus.NOT_CREATED,
        workflow_instance_id="wf-123",
        conversation_id="conv-123",
        created_at=now,
        updated_at=now,
    )

    assert erc.version == 1
    assert erc.sections == {}


def test_should_carry_sections_keyed_by_name() -> None:
    now = datetime.now(UTC)
    erc = Erc(
        erc_id="erc-123",
        schema_version="1.0.0",
        status=ErcLifecycleStatus.READY,
        workflow_instance_id="wf-123",
        conversation_id="conv-123",
        created_at=now,
        updated_at=now,
        sections={"teams": ErcSection(name="teams", status=ErcSectionStatus.COMPLETE)},
    )

    assert erc.sections["teams"].status is ErcSectionStatus.COMPLETE
