from __future__ import annotations

import ast
from pathlib import Path

from pff_fa_ai.common.correlation import new_id
from pff_fa_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pff_fa_ai.engineering_agents.states import AgentResultStatus, FindingSeverity

_SRC_ROOT = Path(__file__).resolve().parents[4] / "src" / "pff_fa_ai"
_AGENT_ID = "architecture-compliance"
_AGENT_VERSION = "1.0.0"

# CLAUDE.md "Layering": "Domain code must never import FastAPI, Langfuse, Azure SDK, a
# provider SDK, or a DB driver directly." These are the module-name prefixes that rule
# forbids inside `domain/` — Pydantic is deliberately not in this list, it's the
# platform's explicit boundary-model standard even inside the domain layer.
_FORBIDDEN_DOMAIN_IMPORT_PREFIXES: tuple[str, ...] = (
    "fastapi",
    "langfuse",
    "azure",
    "redis",
    "httpx",
    "sqlalchemy",
)


def _top_level_module(name: str) -> str:
    return name.split(".", 1)[0]


def _imported_modules(tree: ast.Module) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(_top_level_module(alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(_top_level_module(node.module))
    return modules


class ArchitectureComplianceAgent:
    """doc 23 §48-49/§97-98 (real, deterministic — no model required). Enforces
    CLAUDE.md's "Layering" rule via AST import analysis rather than a semantic model
    judgment, since it's a mechanical, unambiguous rule."""

    agent_id = _AGENT_ID
    version = _AGENT_VERSION

    def __init__(self, *, domain_root: Path | None = None) -> None:
        self._domain_root = domain_root or (_SRC_ROOT / "domain")

    async def run(self) -> EngineeringAgentResult:
        findings: list[Finding] = []
        if not self._domain_root.is_dir():
            return EngineeringAgentResult(
                agent_id=self.agent_id, agent_version=self.version, status=AgentResultStatus.ERROR
            )

        files_scanned = 0
        for path in sorted(self._domain_root.rglob("*.py")):
            files_scanned += 1
            relative = path.relative_to(self._domain_root.parents[1]).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            violations = _imported_modules(tree) & set(_FORBIDDEN_DOMAIN_IMPORT_PREFIXES)
            for module in sorted(violations):
                findings.append(
                    Finding(
                        finding_id=new_id("arch-finding"),
                        agent_id=self.agent_id,
                        severity=FindingSeverity.HIGH,
                        rule="ARCH-DOMAIN-LAYERING",
                        file=relative,
                        description=(
                            f"Domain module imports '{module}', violating CLAUDE.md's layering rule"
                        ),
                        recommendation=(
                            "Move this dependency to an infrastructure/integration "
                            "adapter and inject it into the domain layer through a "
                            "port, rather than importing the framework/SDK directly."
                        ),
                    )
                )

        status = AgentResultStatus.FAIL if findings else AgentResultStatus.PASS
        return EngineeringAgentResult(
            agent_id=self.agent_id,
            agent_version=self.version,
            status=status,
            severity=FindingSeverity.HIGH if findings else None,
            findings=tuple(findings),
            metrics={"files_scanned": float(files_scanned)},
        )
