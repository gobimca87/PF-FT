from pff_fa_ai.engineering_agents.states import AgentResultStatus
from pff_fa_ai.operations.registry import build_default_checklist
from pff_fa_ai.operations.states import CheckFrequency


def test_default_checklist_should_assign_platform_health_and_configuration_to_daily() -> None:
    checklist = build_default_checklist()

    daily_ids = {c.check_id for c in checklist.checks_for(CheckFrequency.DAILY)}

    assert daily_ids == {"platform-health", "configuration"}


def test_default_checklist_should_assign_dependency_to_weekly() -> None:
    checklist = build_default_checklist()

    weekly_ids = {c.check_id for c in checklist.checks_for(CheckFrequency.WEEKLY)}

    assert weekly_ids == {"dependency"}


def test_default_checklist_should_assign_architecture_compliance_to_monthly() -> None:
    checklist = build_default_checklist()

    monthly_ids = {c.check_id for c in checklist.checks_for(CheckFrequency.MONTHLY)}

    assert monthly_ids == {"architecture-compliance"}


async def test_default_checklist_daily_run_should_pass_for_the_real_repo_with_no_health_url() -> (
    None
):
    checklist = build_default_checklist()

    results = await checklist.run_due(CheckFrequency.DAILY)

    statuses = {result.agent_id: result.status for result in results}
    assert statuses["configuration"] is AgentResultStatus.PASS
    assert statuses["platform-health"] is AgentResultStatus.SKIPPED
