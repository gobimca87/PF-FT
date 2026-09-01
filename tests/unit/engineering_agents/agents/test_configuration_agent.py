from pathlib import Path

from pff_fa_ai.engineering_agents.agents.configuration_agent import ConfigurationValidationAgent
from pff_fa_ai.engineering_agents.states import AgentResultStatus, FindingSeverity


async def test_should_pass_for_a_directory_of_valid_config_with_no_secrets(tmp_path: Path) -> None:
    (tmp_path / "base.yaml").write_text("slm:\n  provider: mock\n", encoding="utf-8")
    agent = ConfigurationValidationAgent(config_root=tmp_path)

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()


async def test_should_flag_invalid_yaml_syntax(tmp_path: Path) -> None:
    (tmp_path / "broken.yaml").write_text("slm:\n  provider: [unterminated\n", encoding="utf-8")
    agent = ConfigurationValidationAgent(config_root=tmp_path)

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert result.findings[0].rule == "CONFIG-YAML-SYNTAX"


async def test_should_flag_a_hardcoded_secret(tmp_path: Path) -> None:
    (tmp_path / "service-bus.yaml").write_text(
        'connection: "Bearer eyJhbGciOiJIUzI1NiJ9.abcdefghijklmnopqrstuvwxyz0123"\n',
        encoding="utf-8",
    )
    agent = ConfigurationValidationAgent(config_root=tmp_path)

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert result.severity is FindingSeverity.CRITICAL
    assert any(
        finding.rule and finding.rule.startswith("CONFIG-SECRET-") for finding in result.findings
    )


async def test_should_error_when_the_config_root_does_not_exist(tmp_path: Path) -> None:
    agent = ConfigurationValidationAgent(config_root=tmp_path / "does-not-exist")

    result = await agent.run()

    assert result.status is AgentResultStatus.ERROR


async def test_the_real_config_directory_should_pass_clean() -> None:
    agent = ConfigurationValidationAgent()

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()
