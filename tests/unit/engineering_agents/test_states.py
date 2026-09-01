from pff_fa_ai.engineering_agents.states import (
    FINDING_SEVERITY_RANK,
    AgentLifecycleStatus,
    AgentResultStatus,
    ChangedComponent,
    ExecutionMode,
    FindingSeverity,
    PermissionLevel,
    RemediationMode,
)
from pff_fa_ai.evaluation.states import EvaluationStatus
from pff_fa_ai.guardrails.states import GuardrailSeverity


def test_agent_result_status_should_be_the_same_type_as_evaluation_status() -> None:
    """doc 23 §57 / doc 21 — the two status vocabularies are identical by design."""
    assert AgentResultStatus is EvaluationStatus


def test_finding_severity_should_be_the_same_type_as_guardrail_severity() -> None:
    assert FindingSeverity is GuardrailSeverity


def test_finding_severity_rank_should_cover_every_severity_in_increasing_order() -> None:
    assert set(FINDING_SEVERITY_RANK) == set(FindingSeverity)
    ordered = sorted(FINDING_SEVERITY_RANK, key=lambda severity: FINDING_SEVERITY_RANK[severity])
    assert ordered == [
        FindingSeverity.INFO,
        FindingSeverity.LOW,
        FindingSeverity.MEDIUM,
        FindingSeverity.HIGH,
        FindingSeverity.CRITICAL,
    ]


def test_permission_levels_should_be_ordered_zero_through_five() -> None:
    assert list(PermissionLevel) == sorted(PermissionLevel)
    assert PermissionLevel.LEVEL_0_READ_ONLY.value == 0
    assert PermissionLevel.LEVEL_5_APPROVED_AUTOMATED_REMEDIATION.value == 5


def test_should_define_the_six_documented_execution_modes() -> None:
    assert {mode.value for mode in ExecutionMode} == {
        "READ_ONLY",
        "ANALYZE",
        "VALIDATE",
        "GENERATE",
        "SUGGEST_REMEDIATION",
        "CONTROLLED_MODIFY",
    }


def test_should_define_the_five_documented_remediation_modes() -> None:
    assert {mode.value for mode in RemediationMode} == {
        "REPORT_ONLY",
        "SUGGEST",
        "CREATE_PATCH",
        "CREATE_BRANCH",
        "CREATE_PR",
    }


def test_should_define_the_nine_documented_lifecycle_statuses() -> None:
    assert len(AgentLifecycleStatus) == 9


def test_should_define_all_documented_changed_component_categories() -> None:
    """doc 23 §8's full 21-item list, from "Python code" through "Documentation"."""
    assert len(ChangedComponent) == 21
