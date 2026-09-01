from __future__ import annotations

import json
from typing import Any

from pff_fa_ai.common.correlation import new_id
from pff_fa_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pff_fa_ai.engineering_agents.states import (
    FINDING_SEVERITY_RANK,
    AgentResultStatus,
    FindingSeverity,
)

_AGENT_ID = "security-scan"
_AGENT_VERSION = "1.0.0"

# doc 23 §20-22 (real — parses the *.github/workflows/ci.yml* SAST job's own tool,
# `ruff check . --select S --output-format=json`, into the standard result contract).
# The agent deliberately does not invoke ruff itself (doc 23 §74: avoid unrestricted
# shell access where it isn't strictly required) — the caller (CI, or a developer
# running it locally) captures the tool's real JSON output and passes it in, so this
# agent's own surface area is pure, fully-testable parsing logic with no subprocess risk.
_CRITICAL_CODES = frozenset({"S105", "S106", "S107", "S608"})
_HIGH_CODES = frozenset({"S602", "S603", "S605", "S607", "S324", "S506"})


def _severity_for_code(code: str) -> FindingSeverity:
    if code in _CRITICAL_CODES:
        return FindingSeverity.CRITICAL
    if code in _HIGH_CODES:
        return FindingSeverity.HIGH
    return FindingSeverity.MEDIUM


class SecurityScanAgent:
    """doc 23 §20-23. Findings from ruff's `S` (bandit-derived) ruleset only —
    `detect-secrets` output is a separate, already-committed-baseline workflow
    (`.secrets.baseline`) that doesn't map onto a per-finding contract the same way."""

    agent_id = _AGENT_ID
    version = _AGENT_VERSION

    def __init__(self, *, ruff_json_output: str) -> None:
        self._raw = ruff_json_output

    async def run(self) -> EngineeringAgentResult:
        try:
            entries: list[dict[str, Any]] = json.loads(self._raw)
        except json.JSONDecodeError:
            return EngineeringAgentResult(
                agent_id=self.agent_id, agent_version=self.version, status=AgentResultStatus.ERROR
            )

        findings: list[Finding] = []
        for entry in entries:
            code = entry.get("code")
            if not code:
                continue
            location = entry.get("location") or {}
            findings.append(
                Finding(
                    finding_id=new_id("sec-finding"),
                    agent_id=self.agent_id,
                    severity=_severity_for_code(code),
                    rule=code,
                    file=entry.get("filename"),
                    line=location.get("row"),
                    description=entry.get("message", "Security rule violation"),
                    evidence=entry.get("url"),
                )
            )

        status = AgentResultStatus.FAIL if findings else AgentResultStatus.PASS
        worst = max(
            (finding.severity for finding in findings),
            key=lambda severity: FINDING_SEVERITY_RANK[severity],
            default=None,
        )
        return EngineeringAgentResult(
            agent_id=self.agent_id,
            agent_version=self.version,
            status=status,
            severity=worst,
            findings=tuple(findings),
            metrics={"findings_count": float(len(findings))},
        )
