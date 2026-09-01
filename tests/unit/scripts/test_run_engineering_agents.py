import json
from pathlib import Path

import pytest
from scripts.run_engineering_agents import main, print_report, run_all

from pff_fa_ai.engineering_agents.states import GateStatus


async def test_run_all_should_execute_the_four_wired_agents_against_the_real_repo() -> None:
    results = await run_all(ruff_json_path=None, pip_audit_json_path=None)

    agent_ids = {result.agent_id for result in results}
    assert agent_ids == {"configuration", "architecture-compliance", "security-scan", "dependency"}


async def test_run_all_should_parse_a_provided_ruff_json_file(tmp_path: Path) -> None:
    ruff_json = tmp_path / "ruff.json"
    ruff_json.write_text(
        json.dumps([{"code": "S105", "filename": "x.py", "location": {"row": 1}, "message": "m"}]),
        encoding="utf-8",
    )

    results = await run_all(ruff_json_path=ruff_json, pip_audit_json_path=None)

    security_result = next(r for r in results if r.agent_id == "security-scan")
    assert len(security_result.findings) == 1


def test_main_should_return_zero_when_the_real_repo_passes_clean() -> None:
    exit_code = main([])

    assert exit_code == 0


def test_main_should_return_one_when_a_ruff_json_file_reports_a_critical_finding(
    tmp_path: Path,
) -> None:
    ruff_json = tmp_path / "ruff.json"
    ruff_json.write_text(
        json.dumps(
            [{"code": "S105", "filename": "x.py", "location": {"row": 1}, "message": "leak"}]
        ),
        encoding="utf-8",
    )

    exit_code = main(["--ruff-json", str(ruff_json)])

    assert exit_code == 1


async def test_print_report_should_include_every_agent_id_and_the_overall_gate(
    capsys: pytest.CaptureFixture[str],
) -> None:
    results = await run_all(ruff_json_path=None, pip_audit_json_path=None)

    print_report(results, GateStatus.PASS)

    output = capsys.readouterr().out
    assert "Engineering Validation" in output
    assert "configuration: PASS" in output
    assert "Overall: PASS" in output
