#!/usr/bin/env python
"""doc 23 (Engineering Agents) / DEVELOPMENT-GUIDE Phase 19's "Engineering Agents" CI
stage: runs the real, deterministic engineering agents built in Phase 18 against this
checkout and applies the quality gate, failing CI on a blocking outcome. Lives in
scripts/ (dev/CI helper scripts per DEVELOPMENT-GUIDE §3), not src/pf_ft_ai/, because
it's a CLI entrypoint, not an importable platform capability.

`UnitTestAgent` is deliberately not wired in here — the pipeline's own "Unit Tests"
stage (a separate, earlier `pytest` step) already gates on pass/fail directly; adding a
second, redundant enforcement path here would need parsing a coverage/JUnit report for
no real gain.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from pf_ft_ai.engineering_agents.agents import (
    ArchitectureComplianceAgent,
    ConfigurationValidationAgent,
    DependencyVulnerabilityAgent,
    SecurityScanAgent,
)
from pf_ft_ai.engineering_agents.gate import QualityGateConfig, evaluate_quality_gate
from pf_ft_ai.engineering_agents.models import EngineeringAgentResult
from pf_ft_ai.engineering_agents.states import GateStatus


def _read_json_output(path: Path | None, *, default: str) -> str:
    if path is None:
        return default
    return path.read_text(encoding="utf-8")


async def run_all(
    *, ruff_json_path: Path | None, pip_audit_json_path: Path | None
) -> tuple[EngineeringAgentResult, ...]:
    ruff_json = _read_json_output(ruff_json_path, default="[]")
    pip_audit_json = _read_json_output(pip_audit_json_path, default='{"dependencies": []}')

    agents = (
        ConfigurationValidationAgent(),
        ArchitectureComplianceAgent(),
        SecurityScanAgent(ruff_json_output=ruff_json),
        DependencyVulnerabilityAgent(pip_audit_json_output=pip_audit_json),
    )
    return tuple(await asyncio.gather(*(agent.run() for agent in agents)))


def print_report(results: tuple[EngineeringAgentResult, ...], gate_status: GateStatus) -> None:
    """doc 23 §65 PR comment structure, rendered as plain CI log output."""
    print("Engineering Validation\n")
    for result in results:
        print(f"{result.agent_id}: {result.status.value}")
        for finding in result.findings:
            location = f"{finding.file}:{finding.line}" if finding.file else "-"
            print(
                f"  [{finding.severity.value}] {finding.rule or '-'} {location} "
                f"— {finding.description}"
            )
    print(f"\nOverall: {gate_status.value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ruff-json", type=Path, default=None)
    parser.add_argument("--pip-audit-json", type=Path, default=None)
    args = parser.parse_args(argv)

    results = asyncio.run(
        run_all(ruff_json_path=args.ruff_json, pip_audit_json_path=args.pip_audit_json)
    )
    config = QualityGateConfig(required_agent_ids=frozenset(result.agent_id for result in results))
    outcome = evaluate_quality_gate(results=results, config=config)
    print_report(results, outcome.status)
    if outcome.blocking_reasons:
        print("Blocking reasons:", ", ".join(outcome.blocking_reasons))
    return 1 if outcome.status is GateStatus.FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
