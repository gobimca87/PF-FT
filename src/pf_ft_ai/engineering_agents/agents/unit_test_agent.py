from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pf_ft_ai.engineering_agents.states import (
    FINDING_SEVERITY_RANK,
    AgentResultStatus,
    FindingSeverity,
)

_AGENT_ID = "unit-test"
_AGENT_VERSION = "1.0.0"


class ExecutionSummary(BaseModel):
    """doc 23 §14: the agent's real inputs are the test run's own outputs (passed
    count, coverage report), not something it re-derives by re-running pytest itself
    from inside a pytest process — that would be self-referential and fragile. A real
    CI wiring populates this from the same `pytest -q --cov=...` invocation already
    configured in `pyproject.toml`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    errors: int = Field(ge=0)
    skipped: int = Field(ge=0)
    coverage_percent: float = Field(ge=0, le=100)
    files_below_coverage_threshold: tuple[str, ...] = Field(default_factory=tuple)


class UnitTestAgent:
    """doc 23 §13/§15-16 (real — reports what already ran; does not generate tests,
    since that requires an approved model — see README.md's Engineering Agents
    section). Never weakens a
    result to force a PASS (doc 23 §16, §21 "Unit Test Agent must never weaken tests to
    obtain a pass") — it only reports the summary it was given."""

    agent_id = _AGENT_ID
    version = _AGENT_VERSION

    def __init__(
        self, *, summary: ExecutionSummary, minimum_coverage_percent: float = 80.0
    ) -> None:
        self._summary = summary
        self._minimum_coverage_percent = minimum_coverage_percent

    async def run(self) -> EngineeringAgentResult:
        summary = self._summary
        findings: list[Finding] = []
        if summary.failed > 0 or summary.errors > 0:
            findings.append(
                Finding(
                    finding_id=new_id("test-finding"),
                    agent_id=self.agent_id,
                    severity=FindingSeverity.CRITICAL,
                    rule="TEST-FAILURES",
                    description=f"{summary.failed} test failure(s), {summary.errors} error(s)",
                )
            )
        if summary.coverage_percent < self._minimum_coverage_percent:
            findings.append(
                Finding(
                    finding_id=new_id("test-finding"),
                    agent_id=self.agent_id,
                    severity=FindingSeverity.MEDIUM,
                    rule="TEST-COVERAGE-BELOW-THRESHOLD",
                    description=(
                        f"Coverage {summary.coverage_percent:.1f}% is below the "
                        f"{self._minimum_coverage_percent:.1f}% minimum"
                    ),
                    evidence=", ".join(summary.files_below_coverage_threshold) or None,
                )
            )

        status = (
            AgentResultStatus.FAIL
            if summary.failed > 0 or summary.errors > 0
            else AgentResultStatus.WARNING
            if summary.coverage_percent < self._minimum_coverage_percent
            else AgentResultStatus.PASS
        )
        severity = max(
            (finding.severity for finding in findings),
            key=lambda item: FINDING_SEVERITY_RANK[item],
            default=None,
        )
        return EngineeringAgentResult(
            agent_id=self.agent_id,
            agent_version=self.version,
            status=status,
            severity=severity,
            findings=tuple(findings),
            metrics={
                "passed": float(summary.passed),
                "failed": float(summary.failed),
                "errors": float(summary.errors),
                "skipped": float(summary.skipped),
                "coverage_percent": summary.coverage_percent,
            },
        )
