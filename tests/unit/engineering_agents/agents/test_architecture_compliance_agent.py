from pathlib import Path

from pff_fa_ai.engineering_agents.agents.architecture_compliance_agent import (
    ArchitectureComplianceAgent,
)
from pff_fa_ai.engineering_agents.states import AgentResultStatus


async def test_should_pass_for_a_domain_module_with_no_forbidden_imports(tmp_path: Path) -> None:
    (tmp_path / "entities.py").write_text(
        "from pydantic import BaseModel\n\n\nclass Club(BaseModel):\n    name: str\n",
        encoding="utf-8",
    )
    agent = ArchitectureComplianceAgent(domain_root=tmp_path)

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()


async def test_should_flag_a_domain_module_that_imports_fastapi(tmp_path: Path) -> None:
    (tmp_path / "entities.py").write_text(
        "from fastapi import APIRouter\n\nrouter = APIRouter()\n", encoding="utf-8"
    )
    agent = ArchitectureComplianceAgent(domain_root=tmp_path)

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert result.findings[0].rule == "ARCH-DOMAIN-LAYERING"
    assert "fastapi" in result.findings[0].description


async def test_should_flag_a_domain_module_that_imports_an_azure_sdk(tmp_path: Path) -> None:
    (tmp_path / "repository.py").write_text("import azure.servicebus\n", encoding="utf-8")
    agent = ArchitectureComplianceAgent(domain_root=tmp_path)

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert any(finding.rule == "ARCH-DOMAIN-LAYERING" for finding in result.findings)


async def test_should_error_when_the_domain_root_does_not_exist(tmp_path: Path) -> None:
    agent = ArchitectureComplianceAgent(domain_root=tmp_path / "does-not-exist")

    result = await agent.run()

    assert result.status is AgentResultStatus.ERROR


async def test_the_real_domain_layer_should_pass_clean() -> None:
    """Enforces CLAUDE.md's own layering rule against the actual `domain/` package."""
    agent = ArchitectureComplianceAgent()

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()
