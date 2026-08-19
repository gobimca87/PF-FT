#!/usr/bin/env python
"""doc 28 §135-137 / DEVELOPMENT-GUIDE Phase 22: "Implement the daily/weekly/monthly
operational checklists as scheduled checks where feasible." Run from a scheduled CI
workflow (`.github/workflows/operational-checks.yml`) rather than on every PR — see
scripts/run_engineering_agents.py for the PR-triggered equivalent this reuses agents
from.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from pf_ft_ai.engineering_agents.models import EngineeringAgentResult
from pf_ft_ai.engineering_agents.states import AgentResultStatus
from pf_ft_ai.operations.registry import build_default_checklist
from pf_ft_ai.operations.states import CheckFrequency


def print_report(frequency: CheckFrequency, results: tuple[EngineeringAgentResult, ...]) -> None:
    print(f"Operational Checklist — {frequency.value}\n")
    for result in results:
        print(f"{result.agent_id}: {result.status.value}")
        for finding in result.findings:
            print(f"  [{finding.severity.value}] {finding.description}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency", choices=[f.value for f in CheckFrequency], required=True)
    parser.add_argument("--pip-audit-json", type=Path, default=None)
    parser.add_argument("--health-url", default=None)
    args = parser.parse_args(argv)

    pip_audit_json_output = (
        args.pip_audit_json.read_text(encoding="utf-8")
        if args.pip_audit_json is not None
        else '{"dependencies": []}'
    )
    checklist = build_default_checklist(
        pip_audit_json_output=pip_audit_json_output, base_url=args.health_url
    )
    frequency = CheckFrequency(args.frequency)
    results = asyncio.run(checklist.run_due(frequency))
    print_report(frequency, results)

    return 1 if any(result.status is AgentResultStatus.FAIL for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
