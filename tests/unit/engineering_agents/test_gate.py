from pf_ft_ai.engineering_agents.gate import QualityGateConfig, evaluate_quality_gate
from pf_ft_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pf_ft_ai.engineering_agents.states import AgentResultStatus, FindingSeverity, GateStatus


def _result(agent_id: str, status: AgentResultStatus, **kwargs: object) -> EngineeringAgentResult:
    return EngineeringAgentResult(
        agent_id=agent_id,
        agent_version="1.0.0",
        status=status,
        **kwargs,  # type: ignore[arg-type]
    )


def test_should_pass_when_no_results_and_no_required_agents() -> None:
    outcome = evaluate_quality_gate(results=(), config=QualityGateConfig())

    assert outcome.status is GateStatus.PASS


def test_should_pass_when_every_agent_passes() -> None:
    results = (
        _result("security-scan", AgentResultStatus.PASS),
        _result("unit-test", AgentResultStatus.PASS),
    )

    outcome = evaluate_quality_gate(results=results, config=QualityGateConfig())

    assert outcome.status is GateStatus.PASS


def test_a_required_agent_failure_should_block_the_gate() -> None:
    config = QualityGateConfig(required_agent_ids=frozenset({"security-scan"}))
    results = (_result("security-scan", AgentResultStatus.FAIL),)

    outcome = evaluate_quality_gate(results=results, config=config)

    assert outcome.status is GateStatus.FAIL
    assert "REQUIRED_AGENT_FAILED:security-scan" in outcome.blocking_reasons


def test_an_optional_agent_failure_should_only_warn() -> None:
    config = QualityGateConfig(required_agent_ids=frozenset({"unit-test"}))
    results = (
        _result("unit-test", AgentResultStatus.PASS),
        _result("documentation", AgentResultStatus.FAIL),
    )

    outcome = evaluate_quality_gate(results=results, config=config)

    assert outcome.status is GateStatus.WARNING
    assert "OPTIONAL_AGENT_FAILED:documentation" in outcome.warning_reasons


def test_a_required_agent_that_never_ran_should_block_the_gate() -> None:
    """doc 23 §116 "Critical Agent Failure" — infra couldn't even execute it."""
    config = QualityGateConfig(required_agent_ids=frozenset({"security-scan"}))

    outcome = evaluate_quality_gate(results=(), config=config)

    assert outcome.status is GateStatus.FAIL
    assert "REQUIRED_AGENT_DID_NOT_RUN:security-scan" in outcome.blocking_reasons


def test_a_required_agent_error_should_block_the_gate() -> None:
    config = QualityGateConfig(required_agent_ids=frozenset({"security-scan"}))
    results = (_result("security-scan", AgentResultStatus.ERROR),)

    outcome = evaluate_quality_gate(results=results, config=config)

    assert outcome.status is GateStatus.FAIL
    assert "REQUIRED_AGENT_ERRORED:security-scan" in outcome.blocking_reasons


def test_an_optional_agent_error_should_only_warn() -> None:
    """doc 23 §117 "Non-Critical Agent Failure"."""
    config = QualityGateConfig(required_agent_ids=frozenset())
    results = (_result("documentation", AgentResultStatus.ERROR),)

    outcome = evaluate_quality_gate(results=results, config=config)

    assert outcome.status is GateStatus.WARNING


def test_a_warning_status_result_should_warn_the_gate() -> None:
    results = (_result("unit-test", AgentResultStatus.WARNING),)

    outcome = evaluate_quality_gate(results=results, config=QualityGateConfig())

    assert outcome.status is GateStatus.WARNING
    assert "AGENT_WARNING:unit-test" in outcome.warning_reasons


def test_a_critical_finding_should_block_the_gate_regardless_of_agent_status() -> None:
    """doc 23 §59 "Critical security issue → FAIL"."""
    finding = Finding(
        finding_id="finding-1",
        agent_id="security-scan",
        severity=FindingSeverity.CRITICAL,
        description="Hardcoded secret",
    )
    results = (
        _result(
            "security-scan",
            AgentResultStatus.FAIL,
            findings=(finding,),
            severity=finding.severity,
        ),
    )

    outcome = evaluate_quality_gate(results=results, config=QualityGateConfig())

    assert outcome.status is GateStatus.FAIL
    assert "CRITICAL_FINDING:finding-1" in outcome.blocking_reasons


def test_a_finding_below_the_severity_block_threshold_should_not_block() -> None:
    finding = Finding(
        finding_id="finding-1",
        agent_id="security-scan",
        severity=FindingSeverity.LOW,
        description="Style nit",
    )
    results = (
        _result(
            "security-scan",
            AgentResultStatus.PASS,
            findings=(finding,),
            severity=finding.severity,
        ),
    )

    outcome = evaluate_quality_gate(results=results, config=QualityGateConfig())

    assert outcome.status is GateStatus.PASS
