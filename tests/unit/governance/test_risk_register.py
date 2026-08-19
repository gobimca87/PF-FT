from datetime import date

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.governance.models import RiskRegisterEntry
from pf_ft_ai.governance.risk_register import RiskRegister
from pf_ft_ai.governance.states import GovernanceRiskLevel, Likelihood, RiskStatus


def _entry(
    risk_id: str = "RISK-001",
    status: RiskStatus = RiskStatus.OPEN,
    review_date: date = date(2026, 12, 1),
) -> RiskRegisterEntry:
    return RiskRegisterEntry(
        risk_id=risk_id,
        capability="Affiliation Agent",
        cause="SLM hallucination",
        impact="Incorrect status communicated",
        likelihood=Likelihood.MEDIUM,
        severity=GovernanceRiskLevel.HIGH,
        owner="ai-platform",
        residual_risk=GovernanceRiskLevel.LOW,
        mitigation="Output guardrail cross-check",
        status=status,
        review_date=review_date,
    )


def test_should_add_and_fetch_an_entry() -> None:
    register = RiskRegister()
    register.add(_entry())

    assert register.get("RISK-001") is not None


def test_should_reject_a_duplicate_risk_id() -> None:
    register = RiskRegister()
    register.add(_entry())

    with pytest.raises(ConfigurationError, match="Duplicate risk register entry"):
        register.add(_entry())


def test_update_status_should_replace_the_stored_entry() -> None:
    register = RiskRegister()
    register.add(_entry())

    updated = register.update_status("RISK-001", RiskStatus.MITIGATED)

    assert updated.status is RiskStatus.MITIGATED
    assert register.get("RISK-001").status is RiskStatus.MITIGATED  # type: ignore[union-attr]


def test_update_status_should_reject_an_unknown_risk_id() -> None:
    register = RiskRegister()

    with pytest.raises(ConfigurationError, match="Unknown risk register entry"):
        register.update_status("does-not-exist", RiskStatus.CLOSED)


def test_all_entries_should_return_every_added_entry() -> None:
    register = RiskRegister()
    register.add(_entry("RISK-001"))
    register.add(_entry("RISK-002"))

    assert {entry.risk_id for entry in register.all_entries()} == {"RISK-001", "RISK-002"}


def test_by_status_should_filter_correctly() -> None:
    register = RiskRegister()
    register.add(_entry("RISK-001", RiskStatus.OPEN))
    register.add(_entry("RISK-002", RiskStatus.CLOSED))

    open_risks = register.by_status(RiskStatus.OPEN)

    assert {entry.risk_id for entry in open_risks} == {"RISK-001"}


def test_overdue_for_review_should_include_entries_past_their_review_date() -> None:
    register = RiskRegister()
    register.add(_entry("RISK-001", review_date=date(2026, 1, 1)))
    register.add(_entry("RISK-002", review_date=date(2027, 1, 1)))

    overdue = register.overdue_for_review(as_of=date(2026, 8, 19))

    assert {entry.risk_id for entry in overdue} == {"RISK-001"}


def test_overdue_for_review_should_exclude_closed_entries() -> None:
    register = RiskRegister()
    register.add(_entry("RISK-001", RiskStatus.CLOSED, review_date=date(2026, 1, 1)))

    overdue = register.overdue_for_review(as_of=date(2026, 8, 19))

    assert overdue == ()
