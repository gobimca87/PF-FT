from __future__ import annotations

from functools import partial

from pff_fa_ai.operations.checklist import OperationalCheck, OperationalChecklistRunner
from pff_fa_ai.operations.checks import (
    architecture_check,
    configuration_check,
    dependency_check,
    platform_health_check,
)
from pff_fa_ai.operations.states import CheckFrequency


def build_default_checklist(
    *, pip_audit_json_output: str = '{"dependencies": []}', base_url: str | None = None
) -> OperationalChecklistRunner:
    """doc 28 §135-137 — cadence assignment follows the doc's own checklist item
    placement: "Platform health" is daily (§135); "Vulnerability status" is weekly
    (§136); "Architecture changes"/"Runbook review" are monthly (§137). Configuration
    validity has no single named slot in the doc but is a foundational health signal
    (doc 28 §103-104 "Configuration Failure"/"Configuration Drift" can appear at any
    time), so it runs daily alongside platform health."""
    runner = OperationalChecklistRunner()
    runner.register(
        OperationalCheck(
            check_id="platform-health",
            frequency=CheckFrequency.DAILY,
            description="doc 28 §135 daily checklist: platform health",
            run=partial(platform_health_check, base_url=base_url),
        )
    )
    runner.register(
        OperationalCheck(
            check_id="configuration",
            frequency=CheckFrequency.DAILY,
            description="doc 28 §103-104: configuration validity and drift",
            run=configuration_check,
        )
    )
    runner.register(
        OperationalCheck(
            check_id="dependency",
            frequency=CheckFrequency.WEEKLY,
            description="doc 28 §136 weekly checklist: vulnerability status",
            run=partial(dependency_check, pip_audit_json_output=pip_audit_json_output),
        )
    )
    runner.register(
        OperationalCheck(
            check_id="architecture-compliance",
            frequency=CheckFrequency.MONTHLY,
            description="doc 28 §137 monthly checklist: architecture changes / runbook review",
            run=architecture_check,
        )
    )
    return runner
