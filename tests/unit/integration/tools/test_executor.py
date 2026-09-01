from collections.abc import Callable

import httpx

from pff_fa_ai.common.claims import ClaimsContext
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
from pff_fa_ai.integration.errors.codes import IntegrationErrorCode
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

FAST_RETRY = RetrySettings(
    max_attempts=3, backoff="exponential", initial_ms=1, max_ms=2, jitter=False
)
LENIENT_CIRCUIT = CircuitBreakerSettings(
    failure_threshold=3, cooldown_seconds=30, half_open_max_calls=1
)


def _api_entry(
    *,
    operation: ApiOperation = ApiOperation.READ,
    retryable: bool = True,
    idempotent: bool = True,
) -> ApiCatalogEntry:
    return ApiCatalogEntry(
        api_id="enterprise.club.get",
        name="Get Club",
        version="v1",
        owner="club-service",
        domain="club",
        operation=operation,
        endpoint=ApiEndpoint(method="GET", path="/api/v1/clubs/{clubId}"),
        authorization=ApiAuthorization(required=True, claims=("club.read",)),
        execution=ApiExecutionPolicy(
            idempotent=idempotent, retryable=retryable, parallelizable=True
        ),
    )


def _tool_definition(
    *, idempotent: bool = True, allowed_agents: tuple[str, ...] = ("affiliation_agent",)
) -> ToolDefinition:
    return ToolDefinition(
        tool_id="club.get",
        version="1.0.0",
        description="Get club",
        source=ToolSource(api_id="enterprise.club.get"),
        input_schema_ref="ClubGetRequest",
        output_schema_ref="ClubContext",
        execution_policy=ToolExecutionPolicy(timeout_ms=10000, idempotent=idempotent),
        allowed_agents=allowed_agents,
    )


def _claims(
    permissions: tuple[str, ...] = ("club.read",), *, access_token: str | None = None
) -> ClaimsContext:
    return ClaimsContext(
        subject="user-1", organization="club-1", permissions=permissions, access_token=access_token
    )


def _request(**overrides: object) -> ToolExecutionRequest:
    defaults: dict[str, object] = {
        "tool_id": "club.get",
        "agent_id": "affiliation_agent",
        "claims": _claims(),
        "arguments": {"clubId": "club-123"},
        "workflow_instance_id": "wf-1",
        "operation_id": "get-club",
    }
    defaults.update(overrides)
    return ToolExecutionRequest.model_validate(defaults)


def _build_executor(
    *,
    handler: Callable[[httpx.Request], httpx.Response],
    api_entry: ApiCatalogEntry | None = None,
    tool_definition: ToolDefinition | None = None,
    retry_settings: RetrySettings = FAST_RETRY,
    circuit_breaker_settings: CircuitBreakerSettings = LENIENT_CIRCUIT,
) -> tuple[ToolExecutor, httpx.AsyncClient]:
    entry = api_entry or _api_entry()
    catalog = ApiCatalog([entry])
    registry = ToolRegistry()
    registry.register(tool_definition or _tool_definition(), catalog=catalog)

    transport = httpx.MockTransport(handler)
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
        retry_settings=retry_settings,
        circuit_breaker_settings=circuit_breaker_settings,
        concurrency_limiter=concurrency,
    )
    return executor, async_client


async def test_should_complete_a_successful_call() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"clubId": "club-123", "status": "ACTIVE"})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.TOOL_COMPLETED
    assert result.data == {"clubId": "club-123", "status": "ACTIVE"}


async def test_should_propagate_the_apim_validated_token_to_the_enterprise_call() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(200, json={"clubId": "club-123"})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request(claims=_claims(access_token="apim-issued-token")))

    assert result.status is ToolCallStatus.TOOL_COMPLETED
    assert captured_headers.get("authorization") == "Bearer apim-issued-token"


async def test_should_omit_authorization_header_when_no_token_was_propagated() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(200, json={"clubId": "club-123"})

    executor, client = _build_executor(handler=handler)
    async with client:
        await executor.execute(_request())

    assert "authorization" not in captured_headers


async def test_should_reject_an_unregistered_tool() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request(tool_id="does.not.exist"))

    assert result.status is ToolCallStatus.REJECTED
    assert result.error is not None
    assert "not registered" in result.error.message


async def test_should_reject_an_agent_not_in_the_allow_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request(agent_id="unapproved_agent"))

    assert result.status is ToolCallStatus.REJECTED
    assert result.error is not None
    assert "not permitted" in result.error.message


async def test_should_reject_when_tool_references_an_api_missing_from_the_catalog() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    # register without catalog validation, then execute against a catalog that lacks the API
    entry = _api_entry()
    registry = ToolRegistry()
    registry.register(_tool_definition())
    empty_catalog = ApiCatalog()
    transport = httpx.MockTransport(handler)
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
        api_catalog=empty_catalog,
        http_client=HttpxEnterpriseHttpClient(async_client),
        retry_settings=FAST_RETRY,
        circuit_breaker_settings=LENIENT_CIRCUIT,
        concurrency_limiter=concurrency,
    )
    async with async_client:
        result = await executor.execute(_request())

    assert entry.api_id  # the entry exists; it simply isn't in this executor's catalog
    assert result.status is ToolCallStatus.REJECTED
    assert result.error is not None
    assert "unknown api_id" in result.error.message


async def test_should_reject_when_required_claims_are_missing() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request(claims=_claims(permissions=())))

    assert result.status is ToolCallStatus.REJECTED
    assert result.error is not None
    assert "Missing required claims" in result.error.message


async def test_should_retry_a_retryable_failure_then_succeed() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"clubId": "club-123"})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.TOOL_COMPLETED
    assert call_count == 2


async def test_should_not_retry_a_non_retryable_failure() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(404, json={"error": "not found"})

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.FAILED
    assert call_count == 1
    assert result.error is not None
    assert result.error.retryable is False


async def test_should_fail_after_exhausting_the_retry_budget() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(503)

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.FAILED
    assert call_count == FAST_RETRY.max_attempts


async def test_should_skip_a_write_call_already_completed_idempotently() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json={"status": "submitted"})

    executor, client = _build_executor(
        handler=handler,
        api_entry=_api_entry(operation=ApiOperation.WRITE),
        tool_definition=_tool_definition(idempotent=True),
    )
    async with client:
        first = await executor.execute(_request())
        second = await executor.execute(_request())  # same workflow/operation id

    assert first.status is ToolCallStatus.TOOL_COMPLETED
    assert second.status is ToolCallStatus.TOOL_COMPLETED
    assert call_count == 1  # the enterprise write was never repeated


async def test_should_classify_a_transport_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out", request=request)

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.FAILED
    assert result.error is not None
    assert result.error.code is IntegrationErrorCode.TIMEOUT


async def test_should_classify_a_generic_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.FAILED
    assert result.error is not None
    assert result.error.code is IntegrationErrorCode.DEPENDENCY_ERROR


async def test_should_classify_an_unexpected_error_as_unknown() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise RuntimeError("something unexpected")

    executor, client = _build_executor(handler=handler)
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.FAILED
    assert result.error is not None
    assert result.error.code is IntegrationErrorCode.UNKNOWN


async def test_should_mark_idempotent_write_failed_when_the_call_fails() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "not found"})

    executor, client = _build_executor(
        handler=handler,
        api_entry=_api_entry(operation=ApiOperation.WRITE),
        tool_definition=_tool_definition(idempotent=True),
    )
    async with client:
        result = await executor.execute(_request())

    assert result.status is ToolCallStatus.FAILED


async def test_should_mark_idempotent_write_failed_when_the_circuit_is_open() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    tight_retry = RetrySettings(
        max_attempts=1, backoff="exponential", initial_ms=1, max_ms=1, jitter=False
    )
    tight_circuit = CircuitBreakerSettings(
        failure_threshold=1, cooldown_seconds=30, half_open_max_calls=1
    )
    executor, client = _build_executor(
        handler=handler,
        api_entry=_api_entry(operation=ApiOperation.WRITE),
        tool_definition=_tool_definition(idempotent=True),
        retry_settings=tight_retry,
        circuit_breaker_settings=tight_circuit,
    )
    async with client:
        first = await executor.execute(_request(operation_id="op-1"))
        second = await executor.execute(_request(operation_id="op-2"))

    assert first.status is ToolCallStatus.FAILED
    assert second.status is ToolCallStatus.REJECTED


async def test_should_trip_the_circuit_after_the_failure_threshold() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(503)

    tight_retry = RetrySettings(
        max_attempts=1, backoff="exponential", initial_ms=1, max_ms=1, jitter=False
    )
    tight_circuit = CircuitBreakerSettings(
        failure_threshold=1, cooldown_seconds=30, half_open_max_calls=1
    )
    executor, client = _build_executor(
        handler=handler, retry_settings=tight_retry, circuit_breaker_settings=tight_circuit
    )
    async with client:
        first = await executor.execute(_request())
        calls_after_first = call_count
        second = await executor.execute(_request())

    assert first.status is ToolCallStatus.FAILED
    assert second.status is ToolCallStatus.REJECTED
    assert second.error is not None
    assert "Circuit open" in second.error.message
    assert call_count == calls_after_first  # circuit blocked the second call before HTTP
