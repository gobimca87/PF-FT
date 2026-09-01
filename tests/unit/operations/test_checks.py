import json

import httpx

from pff_fa_ai.engineering_agents.states import AgentResultStatus
from pff_fa_ai.operations.checks import (
    architecture_check,
    configuration_check,
    dependency_check,
    platform_health_check,
)


async def test_configuration_check_should_pass_for_the_real_repo() -> None:
    result = await configuration_check()

    assert result.status is AgentResultStatus.PASS


async def test_architecture_check_should_pass_for_the_real_repo() -> None:
    result = await architecture_check()

    assert result.status is AgentResultStatus.PASS


async def test_dependency_check_should_parse_the_given_pip_audit_output() -> None:
    raw = json.dumps({"dependencies": [{"name": "pkg", "version": "1.0", "vulns": []}]})

    result = await dependency_check(pip_audit_json_output=raw)

    assert result.status is AgentResultStatus.PASS
    assert result.metrics["dependencies_scanned"] == 1.0


async def test_platform_health_check_should_skip_when_no_base_url_configured() -> None:
    result = await platform_health_check(base_url=None)

    assert result.status is AgentResultStatus.SKIPPED


async def test_platform_health_check_should_pass_for_a_200_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "READY"})

    result = await platform_health_check(
        base_url="https://platform.example", transport=httpx.MockTransport(handler)
    )

    assert result.status is AgentResultStatus.PASS


async def test_platform_health_check_should_fail_for_a_non_200_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    result = await platform_health_check(
        base_url="https://platform.example", transport=httpx.MockTransport(handler)
    )

    assert result.status is AgentResultStatus.FAIL
    assert result.findings[0].description == "Health endpoint returned HTTP 503"


async def test_platform_health_check_should_error_when_the_endpoint_is_unreachable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    result = await platform_health_check(
        base_url="https://platform.example", transport=httpx.MockTransport(handler)
    )

    assert result.status is AgentResultStatus.ERROR
