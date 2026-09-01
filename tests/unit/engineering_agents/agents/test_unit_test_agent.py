from pff_fa_ai.engineering_agents.agents.unit_test_agent import ExecutionSummary, UnitTestAgent
from pff_fa_ai.engineering_agents.states import AgentResultStatus, FindingSeverity


def _summary(**overrides: object) -> ExecutionSummary:
    defaults: dict[str, object] = {
        "passed": 100,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "coverage_percent": 95.0,
    }
    defaults.update(overrides)
    return ExecutionSummary.model_validate(defaults)


async def test_should_pass_when_no_failures_and_coverage_meets_the_minimum() -> None:
    agent = UnitTestAgent(summary=_summary())

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()


async def test_should_fail_when_there_are_test_failures() -> None:
    agent = UnitTestAgent(summary=_summary(failed=2))

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert result.severity is FindingSeverity.CRITICAL
    assert result.findings[0].rule == "TEST-FAILURES"


async def test_should_fail_when_there_are_errors_even_with_no_failures() -> None:
    agent = UnitTestAgent(summary=_summary(errors=1))

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL


async def test_should_warn_when_coverage_is_below_the_configured_minimum() -> None:
    agent = UnitTestAgent(summary=_summary(coverage_percent=60.0), minimum_coverage_percent=80.0)

    result = await agent.run()

    assert result.status is AgentResultStatus.WARNING
    assert result.findings[0].rule == "TEST-COVERAGE-BELOW-THRESHOLD"


async def test_failures_should_take_priority_over_a_coverage_warning() -> None:
    agent = UnitTestAgent(
        summary=_summary(failed=1, coverage_percent=10.0), minimum_coverage_percent=80.0
    )

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert len(result.findings) == 2


async def test_metrics_should_report_the_full_summary() -> None:
    agent = UnitTestAgent(summary=_summary(passed=42, skipped=3))

    result = await agent.run()

    assert result.metrics["passed"] == 42.0
    assert result.metrics["skipped"] == 3.0
    assert result.metrics["coverage_percent"] == 95.0
