import httpx

from pff_fa_ai.integration.api.catalog import (
    ApiAuthorization,
    ApiCatalogEntry,
    ApiEndpoint,
    ApiExecutionPolicy,
    ApiOperation,
)
from pff_fa_ai.integration.api.client import HttpxEnterpriseHttpClient

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


async def test_should_substitute_path_parameters_and_return_json_body() -> None:
    captured_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_urls.append(str(request.url))
        return httpx.Response(200, json={"clubId": "club-123", "status": "ACTIVE"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://enterprise.example"
    ) as async_client:
        client = HttpxEnterpriseHttpClient(async_client)
        response = await client.request(entry=ENTRY, path_params={"clubId": "club-123"})

    assert response.status_code == 200
    assert response.body == {"clubId": "club-123", "status": "ACTIVE"}
    assert captured_urls[0].endswith("/api/v1/clubs/club-123")


async def test_should_fall_back_to_text_body_for_non_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://enterprise.example"
    ) as async_client:
        client = HttpxEnterpriseHttpClient(async_client)
        response = await client.request(entry=ENTRY, path_params={"clubId": "club-123"})

    assert response.body == "not json"


async def test_should_propagate_error_status_codes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "not found"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://enterprise.example"
    ) as async_client:
        client = HttpxEnterpriseHttpClient(async_client)
        response = await client.request(entry=ENTRY, path_params={"clubId": "missing"})

    assert response.status_code == 404
