from pff_fa_ai.agents.affiliation.states import (
    TERMINAL_STATUSES,
    WAITING_STATUSES,
    AffiliationApplicationStatus,
)


def test_should_define_the_six_documented_application_statuses() -> None:
    assert {status.value for status in AffiliationApplicationStatus} == {
        "IN_PROGRESS",
        "PENDING_CFA",
        "INVOICED",
        "COMPLETE",
        "REJECTED",
        "CANCELLED",
    }


def test_waiting_and_terminal_statuses_should_be_disjoint() -> None:
    assert WAITING_STATUSES.isdisjoint(TERMINAL_STATUSES)


def test_waiting_and_terminal_statuses_should_cover_five_of_the_six_statuses() -> None:
    covered = WAITING_STATUSES | TERMINAL_STATUSES
    uncovered = set(AffiliationApplicationStatus) - covered
    assert uncovered == {AffiliationApplicationStatus.IN_PROGRESS}
