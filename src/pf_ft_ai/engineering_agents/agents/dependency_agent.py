from __future__ import annotations

import json
from typing import Any

from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pf_ft_ai.engineering_agents.states import (
    FINDING_SEVERITY_RANK,
    AgentResultStatus,
    FindingSeverity,
)

_AGENT_ID = "dependency"
_AGENT_VERSION = "1.0.0"


class DependencyVulnerabilityAgent:
    """doc 23 §24-26 (real — parses `pip-audit --format=json` output, the same tool
    `.github/workflows/ci.yml`'s dependency-scan job already runs). No fix
    available for a known vulnerability is treated as CRITICAL (unpatchable exposure);
    a vulnerability with a fix available is HIGH (doc 23 §26 "Exploitability,
    Exposure... Compensating controls" — an available upgrade is itself a mitigating
    factor relative to no fix existing at all)."""

    agent_id = _AGENT_ID
    version = _AGENT_VERSION

    def __init__(self, *, pip_audit_json_output: str) -> None:
        self._raw = pip_audit_json_output

    async def run(self) -> EngineeringAgentResult:
        try:
            report: dict[str, Any] = json.loads(self._raw)
        except json.JSONDecodeError:
            return EngineeringAgentResult(
                agent_id=self.agent_id, agent_version=self.version, status=AgentResultStatus.ERROR
            )

        findings: list[Finding] = []
        for dependency in report.get("dependencies", []):
            name = dependency.get("name", "unknown")
            version = dependency.get("version", "unknown")
            for vuln in dependency.get("vulns", []):
                fix_versions = vuln.get("fix_versions") or []
                severity = FindingSeverity.CRITICAL if not fix_versions else FindingSeverity.HIGH
                vuln_description = vuln.get("description", "known vulnerability")
                findings.append(
                    Finding(
                        finding_id=new_id("dep-finding"),
                        agent_id=self.agent_id,
                        severity=severity,
                        rule=vuln.get("id", "UNKNOWN-VULN"),
                        description=f"{name} {version}: {vuln_description}",
                        evidence=vuln.get("id"),
                        recommendation=(
                            f"Upgrade to one of: {', '.join(fix_versions)}"
                            if fix_versions
                            else "No fix currently published — track upstream advisory."
                        ),
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
            metrics={
                "dependencies_scanned": float(len(report.get("dependencies", []))),
                "vulnerabilities_found": float(len(findings)),
            },
        )
