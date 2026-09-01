import pytest
from pydantic import ValidationError

from pff_fa_ai.agents.affiliation.models import ApplicationSummary, ClubSummary
from pff_fa_ai.agents.affiliation.states import AffiliationApplicationStatus


def test_application_summary_should_default_optional_fields() -> None:
    summary = ApplicationSummary(
        application_id="app-1",
        club_id="club-1",
        season="2026-27",
        status=AffiliationApplicationStatus.IN_PROGRESS,
        total_fee=100.0,
    )

    assert summary.currency == "GBP"
    assert summary.invoice_number is None
    assert summary.is_cfa_review_required is False
    assert summary.rejection_reason is None


def test_application_summary_should_reject_a_negative_fee() -> None:
    with pytest.raises(ValidationError):
        ApplicationSummary(
            application_id="app-1",
            club_id="club-1",
            season="2026-27",
            status=AffiliationApplicationStatus.COMPLETE,
            total_fee=-1.0,
        )


def test_club_summary_should_be_frozen() -> None:
    club = ClubSummary(club_id="club-1", name="Testville FC", county="Testshire", status="ACTIVE")

    with pytest.raises(ValidationError):
        club.name = "Renamed FC"  # type: ignore[misc]
