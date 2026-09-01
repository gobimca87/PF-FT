import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.engineering_agents.models import EngineeringAgentResult
from pff_fa_ai.engineering_agents.states import AgentResultStatus
from pff_fa_ai.operations.checklist import OperationalCheck, OperationalChecklistRunner
from pff_fa_ai.operations.states import CheckFrequency


async def _fake_pass() -> EngineeringAgentResult:
    return EngineeringAgentResult(
        agent_id="fake-check", agent_version="1.0.0", status=AgentResultStatus.PASS
    )


def _check(
    check_id: str = "fake-check", frequency: CheckFrequency = CheckFrequency.DAILY
) -> OperationalCheck:
    return OperationalCheck(
        check_id=check_id, frequency=frequency, description="A fake check", run=_fake_pass
    )


def test_should_register_and_filter_checks_by_frequency() -> None:
    runner = OperationalChecklistRunner()
    runner.register(_check("daily-1", CheckFrequency.DAILY))
    runner.register(_check("weekly-1", CheckFrequency.WEEKLY))

    daily = runner.checks_for(CheckFrequency.DAILY)

    assert {c.check_id for c in daily} == {"daily-1"}


def test_should_reject_a_duplicate_check_id() -> None:
    runner = OperationalChecklistRunner()
    runner.register(_check())

    with pytest.raises(ConfigurationError, match="Duplicate operational check"):
        runner.register(_check())


async def test_run_due_should_execute_only_checks_for_the_given_frequency() -> None:
    runner = OperationalChecklistRunner()
    runner.register(_check("daily-1", CheckFrequency.DAILY))
    runner.register(_check("monthly-1", CheckFrequency.MONTHLY))

    results = await runner.run_due(CheckFrequency.DAILY)

    assert len(results) == 1
    assert results[0].agent_id == "fake-check"


async def test_run_due_should_return_empty_for_a_frequency_with_no_checks() -> None:
    runner = OperationalChecklistRunner()

    results = await runner.run_due(CheckFrequency.WEEKLY)

    assert results == ()
