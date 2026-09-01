"""doc 22 §81/§133 "Resilience Testing" / "Availability Testing": when one dependency
fails, the others must keep working — verified here with real `SlmService` and
`ToolExecutor` instances running side by side (each already owns its own independent
`CircuitBreaker`; `tests/unit/observability/test_resilience.py` already proves
`ResilienceRegistry` hands out isolated breakers — this test proves that isolation holds
for the actual dependency-facing services built on top of it, not just the registry)."""

from collections.abc import AsyncIterator

import httpx
import pytest

from pff_fa_ai.common.exceptions import ModelError
from pff_fa_ai.configuration.models import (
    CircuitBreakerSettings,
    ConcurrencyPoolSettings,
    ConcurrencySettings,
    RetrySettings,
)
from pff_fa_ai.integration.api.catalog import (
    ApiAuthorization,
    ApiCatalog,
    ApiCatalogEntry,
    ApiEndpoint,
    ApiExecutionPolicy,
    ApiOperation,
)
from pff_fa_ai.integration.api.client import HttpxEnterpriseHttpClient
from pff_fa_ai.integration.execution.concurrency import ConcurrencyLimiter
from pff_fa_ai.integration.tools.executor import ToolExecutor
from pff_fa_ai.integration.tools.models import (
    ToolDefinition,
    ToolExecutionPolicy,
    ToolExecutionRequest,
    ToolSource,
)
from pff_fa_ai.integration.tools.registry import ToolRegistry
from pff_fa_ai.integration.tools.states import ToolCallStatus
from pff_fa_ai.slm.models import SlmMessage, SlmRequest, SlmResponse
from pff_fa_ai.slm.service import SlmService
from pff_fa_ai.slm.states import ProviderHealthStatus
from tests.fixtures.factories import make_claims

_TIGHT_RETRY = RetrySettings(
    max_attempts=1, backoff="exponential", initial_ms=1, max_ms=1, jitter=False
)
_TIGHT_CIRCUIT = CircuitBreakerSettings(
    failure_threshold=1, cooldown_seconds=30, half_open_max_calls=1
)


class _AlwaysFailingSlmProvider:
    async def generate(self, request: SlmRequest) -> SlmResponse:
        raise ModelError("primary SLM provider unavailable")

    def stream(self, request: SlmRequest) -> AsyncIterator[str]:
        raise NotImplementedError

    async def health(self) -> ProviderHealthStatus:
        return ProviderHealthStatus.UNAVAILABLE


def _slm_request() -> SlmRequest:
    return SlmRequest(
        model_id="mock-slm-v1",
        messages=(SlmMessage(role="user", content="hello"),),
        temperature=0.2,
        top_p=1.0,
        max_output_tokens=64,
    )


def _tool_request() -> ToolExecutionRequest:
    return ToolExecutionRequest(
        tool_id="club.get",
        agent_id="affiliation_agent",
        claims=make_claims(permissions=("club.read",)),
        arguments={"clubId": "club-123"},
        workflow_instance_id="wf-1",
        operation_id="get-club",
    )


def _build_tool_executor(transport: httpx.MockTransport) -> tuple[ToolExecutor, httpx.AsyncClient]:
    entry = ApiCatalogEntry(
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
    catalog = ApiCatalog([entry])
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            tool_id="club.get",
            version="1.0.0",
            description="Get club",
            source=ToolSource(api_id="enterprise.club.get"),
            input_schema_ref="ClubGetRequest",
            output_schema_ref="ClubContext",
            execution_policy=ToolExecutionPolicy(timeout_ms=10000, idempotent=True),
            allowed_agents=("affiliation_agent",),
        ),
        catalog=catalog,
    )
    async_client = httpx.AsyncClient(transport=transport, base_url="https://enterprise.example")
    concurrency = ConcurrencyLimiter(
        ConcurrencySettings(
            global_max=20,
            enterprise=ConcurrencyPoolSettings(max_parallel=10),
            mcp=ConcurrencyPoolSettings(max_parallel=5),
        )
    )
    executor = ToolExecutor(
        tool_registry=registry,
        api_catalog=catalog,
        http_client=HttpxEnterpriseHttpClient(async_client),
        retry_settings=_TIGHT_RETRY,
        circuit_breaker_settings=_TIGHT_CIRCUIT,
        concurrency_limiter=concurrency,
    )
    return executor, async_client


async def test_a_failed_slm_dependency_should_not_affect_a_healthy_enterprise_api_call() -> None:
    slm = SlmService(
        _AlwaysFailingSlmProvider(), retry=_TIGHT_RETRY, circuit_breaker=_TIGHT_CIRCUIT
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"clubId": "club-123", "status": "ACTIVE"})

    executor, client = _build_tool_executor(httpx.MockTransport(handler))

    with pytest.raises(ModelError):
        await slm.generate(_slm_request())

    async with client:
        result = await executor.execute(_tool_request())

    assert result.status is ToolCallStatus.TOOL_COMPLETED


async def test_an_open_enterprise_api_circuit_should_not_affect_slm_fallback_behavior() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    executor, client = _build_tool_executor(httpx.MockTransport(handler))

    async with client:
        first = await executor.execute(_tool_request())
        second = await executor.execute(_tool_request())

    assert first.status is ToolCallStatus.FAILED
    assert second.status is ToolCallStatus.REJECTED  # enterprise API circuit is open

    slm = SlmService(
        _AlwaysFailingSlmProvider(), retry=_TIGHT_RETRY, circuit_breaker=_TIGHT_CIRCUIT
    )

    # the SLM's own circuit/failure classification is unaffected by the enterprise API's
    # circuit state — proves the two breakers never cross-contaminate.
    with pytest.raises(ModelError):
        await slm.generate(_slm_request())
