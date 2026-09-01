import pytest
from pydantic import ValidationError

from pff_fa_ai.engineering_agents.models import (
    EngineeringAgentDefinition,
    EngineeringAgentResult,
    EngineeringRun,
    Finding,
)
from pff_fa_ai.engineering_agents.states import (
    AgentLifecycleStatus,
    AgentResultStatus,
    ChangedComponent,
    EngineeringAgentRisk,
    ExecutionMode,
    FindingSeverity,
    PermissionLevel,
)


def _finding(**overrides: object) -> Finding:
    defaults: dict[str, object] = {
        "finding_id": "finding-1",
        "agent_id": "security-scan",
        "severity": FindingSeverity.HIGH,
        "description": "Something bad",
    }
    defaults.update(overrides)
    return Finding.model_validate(defaults)


def test_finding_should_default_optional_fields() -> None:
    finding = _finding()

    assert finding.rule is None
    assert finding.file is None
    assert finding.line is None
    assert finding.auto_remediation_available is False


def test_finding_should_be_frozen() -> None:
    finding = _finding()

    with pytest.raises(ValidationError):
        finding.severity = FindingSeverity.LOW  # type: ignore[misc]


def test_engineering_agent_result_should_default_to_no_findings_and_no_severity() -> None:
    result = EngineeringAgentResult(
        agent_id="security-scan", agent_version="1.0.0", status=AgentResultStatus.PASS
    )

    assert result.severity is None
    assert result.findings == ()
    assert result.metrics == {}


def test_engineering_agent_result_should_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        EngineeringAgentResult(
            agent_id="security-scan",
            agent_version="1.0.0",
            status=AgentResultStatus.PASS,
            unexpected="nope",  # type: ignore[call-arg]
        )


def test_engineering_agent_definition_should_default_model_id_to_none() -> None:
    definition = EngineeringAgentDefinition(
        agent_id="configuration",
        version="1.0.0",
        purpose="Validate config",
        owner="platform-engineering",
        risk=EngineeringAgentRisk.LOW,
        permission_level=PermissionLevel.LEVEL_1_REPORT,
        execution_mode=ExecutionMode.VALIDATE,
        lifecycle_status=AgentLifecycleStatus.ACTIVE,
    )

    assert definition.model_id is None


def test_engineering_run_should_default_optional_collections() -> None:
    run = EngineeringRun(run_id="eng-run-1", repository="pff-fa-ai", commit="abc123")

    assert run.changed_components == ()
    assert run.agent_ids == ()
    assert run.results == ()
    assert run.gate_status is None


def test_engineering_run_should_accept_changed_components() -> None:
    run = EngineeringRun(
        run_id="eng-run-1",
        repository="pff-fa-ai",
        commit="abc123",
        changed_components=(ChangedComponent.PROMPTS, ChangedComponent.RAG),
    )

    assert run.changed_components == (ChangedComponent.PROMPTS, ChangedComponent.RAG)
