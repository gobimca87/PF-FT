import json

from pff_fa_ai.engineering_agents.agents.security_scan_agent import SecurityScanAgent
from pff_fa_ai.engineering_agents.states import AgentResultStatus, FindingSeverity


async def test_should_pass_for_an_empty_findings_list() -> None:
    agent = SecurityScanAgent(ruff_json_output="[]")

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()


async def test_should_parse_a_real_shaped_ruff_finding_into_a_finding() -> None:
    raw = json.dumps([
        {
            "code": "S105",
            "filename": "src/pff_fa_ai/example.py",
            "location": {"row": 1, "column": 12},
            "message": 'Possible hardcoded password assigned to: "password"',
            "url": "https://docs.astral.sh/ruff/rules/hardcoded-password-string",
        }
    ])
    agent = SecurityScanAgent(ruff_json_output=raw)

    result = await agent.run()

    assert result.status is AgentResultStatus.FAIL
    assert result.severity is FindingSeverity.CRITICAL
    finding = result.findings[0]
    assert finding.rule == "S105"
    assert finding.file == "src/pff_fa_ai/example.py"
    assert finding.line == 1
    assert "hardcoded password" in finding.description


async def test_should_classify_a_non_secret_rule_as_medium_severity() -> None:
    raw = json.dumps([
        {
            "code": "S101",
            "filename": "tests/example.py",
            "location": {"row": 5},
            "message": "Use of assert detected",
        }
    ])
    agent = SecurityScanAgent(ruff_json_output=raw)

    result = await agent.run()

    assert result.findings[0].severity is FindingSeverity.MEDIUM


async def test_should_classify_a_subprocess_rule_as_high_severity() -> None:
    raw = json.dumps([
        {
            "code": "S603",
            "filename": "tool.py",
            "location": {"row": 2},
            "message": "subprocess call",
        }
    ])
    agent = SecurityScanAgent(ruff_json_output=raw)

    result = await agent.run()

    assert result.findings[0].severity is FindingSeverity.HIGH


async def test_should_skip_an_entry_with_no_rule_code() -> None:
    raw = json.dumps([{"filename": "tool.py", "location": {"row": 1}, "message": "no code here"}])
    agent = SecurityScanAgent(ruff_json_output=raw)

    result = await agent.run()

    assert result.status is AgentResultStatus.PASS
    assert result.findings == ()


async def test_should_error_for_malformed_json_output() -> None:
    agent = SecurityScanAgent(ruff_json_output="not valid json")

    result = await agent.run()

    assert result.status is AgentResultStatus.ERROR
