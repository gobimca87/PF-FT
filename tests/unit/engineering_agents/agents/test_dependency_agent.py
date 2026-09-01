import json

from pff_fa_ai.engineering_agents.agents.dependency_agent import DependencyVulnerabilityAgent
from pff_fa_ai.engineering_agents.states import AgentResultStatus, FindingSeverity


async def test_should_pass_when_no_dependencies_have_vulnerabilities() -> None:
    raw = json.dumps({"dependencies": [{"name": "fastapi", "version": "0.115.0", "vulns": []}]})
    agent = DependencyVulnerabilityAgent(pip_audit_json_output=raw)

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()


async def test_should_flag_a_vulnerability_with_a_fix_available_as_high() -> None:
    raw = json.dumps({
        "dependencies": [
            {
                "name": "somepkg",
                "version": "1.0.0",
                "vulns": [
                    {
                        "id": "PYSEC-2021-123",
                        "fix_versions": ["1.0.1"],
                        "description": "Remote code execution",
                    }
                ],
            }
        ]
    })
    agent = DependencyVulnerabilityAgent(pip_audit_json_output=raw)

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    finding = result.findings[0]
    assert finding.severity is FindingSeverity.HIGH
    assert finding.rule == "PYSEC-2021-123"
    assert "1.0.1" in (finding.recommendation or "")


async def test_should_flag_a_vulnerability_with_no_fix_available_as_critical() -> None:
    raw = json.dumps({
        "dependencies": [
            {
                "name": "somepkg",
                "version": "1.0.0",
                "vulns": [{"id": "PYSEC-2021-999", "fix_versions": [], "description": "Unpatched"}],
            }
        ]
    })
    agent = DependencyVulnerabilityAgent(pip_audit_json_output=raw)

    result = await agent.run()

    assert result.severity is FindingSeverity.CRITICAL
    assert "No fix" in (result.findings[0].recommendation or "")


async def test_should_error_for_malformed_json_output() -> None:
    agent = DependencyVulnerabilityAgent(pip_audit_json_output="not valid json")

    result = await agent.run()

    assert result.status is AgentResultStatus.ERROR


async def test_metrics_should_report_dependency_and_vulnerability_counts() -> None:
    raw = json.dumps({
        "dependencies": [
            {"name": "a", "version": "1.0", "vulns": []},
            {
                "name": "b",
                "version": "1.0",
                "vulns": [{"id": "X-1", "fix_versions": ["1.1"], "description": "d"}],
            },
        ]
    })
    agent = DependencyVulnerabilityAgent(pip_audit_json_output=raw)

    result = await agent.run()

    assert result.metrics["dependencies_scanned"] == 2.0
    assert result.metrics["vulnerabilities_found"] == 1.0
