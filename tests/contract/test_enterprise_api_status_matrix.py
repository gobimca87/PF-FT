"""doc 22 §20-21 "API Mock Requirements" / DEVELOPMENT-GUIDE Phase 17: the enterprise
API contract boundary (`HttpxEnterpriseHttpClient`) must be verified across the full
status/error space, not just the 200/404 cases `tests/unit/integration/api/test_client.py`
already covers. This is a contract test, not a `ToolExecutor` behavior test — it asserts
only that the client faithfully forwards whatever the enterprise API actually returned,
never reinterpreting or inventing it (CLAUDE.md Golden Rule)."""

from typing import Any

import httpx
import pytest

from pff_fa_ai.integration.api.catalog import (
    ApiAuthorization,
    ApiCatalogEntry,
    ApiEndpoint,
    ApiExecutionPolicy,
    ApiOperation,
)
from pff_fa_ai.integration.api.client import HttpxEnterpriseHttpClient
from tests.mocks.enterprise_api import empty_transport, status_transport, timeout_transport
from tests.stubs.payloads import MALFORMED_JSON_BODY, large_enterprise_list_payload

ENTRY = ApiCatalogEntry(
    api_id="enterprise.club.get",
    name="Get Club",
    version="v1",
    owner="club-service",
    domain="club",
    operation=ApiOperation.READ,
    endpoint=ApiEndpoint(method="GET", path="/api/v1/clubs/{clubId}"),
    authorization=ApiAuthorization(required=True, claims=("club.read",)),
    execution=ApiExecutionPolicy(idempotent=True, retryable=True, parallelizable=True),
)


async def _request(transport: httpx.MockTransport) -> tuple[int, Any]:
    async with httpx.AsyncClient(
        transport=transport, base_url="https://enterprise.example"
    ) as async_client:
        client = HttpxEnterpriseHttpClient(async_client)
        response = await client.request(entry=ENTRY, path_params={"clubId": "club-123"})
    return response.status_code, response.body


@pytest.mark.parametrize("status_code", [200, 201, 400, 401, 403, 404, 409, 429, 500, 502, 503])
async def test_should_faithfully_forward_every_documented_status_code(status_code: int) -> None:
    body = {"status_code": status_code, "clubId": "club-123"}

    actual_status, actual_body = await _request(status_transport(status_code, json_body=body))

    assert actual_status == status_code
    assert actual_body == body


async def test_should_forward_a_partial_response_body_without_inventing_missing_fields() -> None:
    """doc 22 §21 "Partial response" — the client must pass through exactly what was
    returned, not fill in fields the enterprise API omitted."""
    partial_body = {"clubId": "club-123"}  # "status" field is missing from the response

    _status, actual_body = await _request(status_transport(200, json_body=partial_body))

    assert actual_body == partial_body
    assert "status" not in actual_body


async def test_should_fall_back_to_empty_text_for_an_empty_response_body() -> None:
    _status, actual_body = await _request(empty_transport(200))

    assert actual_body == ""


async def test_should_fall_back_to_raw_text_for_a_malformed_json_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=MALFORMED_JSON_BODY)

    _status, actual_body = await _request(httpx.MockTransport(handler))

    assert actual_body == MALFORMED_JSON_BODY


async def test_should_forward_a_large_100_plus_entity_response_body_intact() -> None:
    """doc 22 §127 "Large Data Testing" — the client must never silently truncate."""
    large_body = large_enterprise_list_payload(137, entity_type="team")

    _status, actual_body = await _request(status_transport(200, json_body=large_body))

    assert actual_body["total"] == 137
    assert len(actual_body["items"]) == 137
    assert actual_body["items"][-1]["id"] == "team-137"


async def test_should_propagate_a_timeout_as_an_exception_for_the_retry_layer_to_handle() -> None:
    """The client is a thin transport wrapper — timeout/retry policy is `ToolExecutor`'s
    job (doc 10 §32-34), so a timeout must surface as a real exception here, not a
    silently-swallowed response."""
    async with httpx.AsyncClient(
        transport=timeout_transport(), base_url="https://enterprise.example"
    ) as async_client:
        client = HttpxEnterpriseHttpClient(async_client)
        with pytest.raises(httpx.TimeoutException):
            await client.request(entry=ENTRY, path_params={"clubId": "club-123"})
