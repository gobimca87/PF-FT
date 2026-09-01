from __future__ import annotations

from pathlib import Path

import yaml

from pff_fa_ai.common.correlation import new_id
from pff_fa_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pff_fa_ai.engineering_agents.states import (
    FINDING_SEVERITY_RANK,
    AgentResultStatus,
    FindingSeverity,
)
from pff_fa_ai.guardrails.secrets import detect_secrets

_CONFIG_ROOT = Path(__file__).resolve().parents[4] / "config"
_AGENT_ID = "configuration"
_AGENT_VERSION = "1.0.0"


class ConfigurationValidationAgent:
    """doc 23 §36-37 (real, deterministic — no model required). Validates every YAML
    file under `config/` parses, and scans its raw text for hardcoded secrets using the
    same detector `guardrails.secrets` already applies to runtime content — a config
    file is just as capable of leaking a credential as a prompt or a model output."""

    agent_id = _AGENT_ID
    version = _AGENT_VERSION

    def __init__(self, *, config_root: Path | None = None) -> None:
        self._config_root = config_root or _CONFIG_ROOT

    async def run(self) -> EngineeringAgentResult:
        findings: list[Finding] = []
        if not self._config_root.is_dir():
            return EngineeringAgentResult(
                agent_id=self.agent_id, agent_version=self.version, status=AgentResultStatus.ERROR
            )

        for path in sorted(self._config_root.rglob("*.yaml")):
            relative = path.relative_to(self._config_root.parent).as_posix()
            text = path.read_text(encoding="utf-8")

            try:
                yaml.safe_load(text)
            except yaml.YAMLError as exc:
                findings.append(
                    Finding(
                        finding_id=new_id("cfg-finding"),
                        agent_id=self.agent_id,
                        severity=FindingSeverity.HIGH,
                        rule="CONFIG-YAML-SYNTAX",
                        file=relative,
                        description="File does not parse as valid YAML",
                        evidence=str(exc),
                        recommendation="Fix the YAML syntax error before merging.",
                    )
                )
                continue

            secret_categories = detect_secrets(text)
            for category in sorted(secret_categories):
                findings.append(
                    Finding(
                        finding_id=new_id("cfg-finding"),
                        agent_id=self.agent_id,
                        severity=FindingSeverity.CRITICAL,
                        rule=f"CONFIG-SECRET-{category}",
                        file=relative,
                        description="Configuration file appears to contain a hardcoded secret",
                        recommendation=(
                            "Replace the literal value with a `*_secret_ref` entry "
                            "resolved via SecretResolver (CLAUDE.md secrets rule)."
                        ),
                    )
                )

        status = AgentResultStatus.FAIL if findings else AgentResultStatus.PASS
        worst_severity = max(
            (finding.severity for finding in findings),
            key=lambda severity: FINDING_SEVERITY_RANK[severity],
            default=None,
        )
        return EngineeringAgentResult(
            agent_id=self.agent_id,
            agent_version=self.version,
            status=status,
            severity=worst_severity,
            findings=tuple(findings),
            metrics={"files_scanned": float(len(list(self._config_root.rglob("*.yaml"))))},
        )
