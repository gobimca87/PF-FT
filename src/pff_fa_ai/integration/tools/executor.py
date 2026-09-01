from __future__ import annotations

import httpx

from pff_fa_ai.configuration.models import CircuitBreakerSettings, RetrySettings
from pff_fa_ai.integration.api.catalog import ApiCatalog, ApiOperation
from pff_fa_ai.integration.api.client import EnterpriseApiResponse, EnterpriseHttpClient
from pff_fa_ai.integration.errors.codes import (
    IntegrationErrorCode,
    classify_http_status,
    is_retryable,
)
from pff_fa_ai.integration.execution.circuit import CircuitBreaker
from pff_fa_ai.integration.execution.concurrency import ConcurrencyLimiter
from pff_fa_ai.integration.execution.idempotency import (
    IdempotencyStore,
    InMemoryIdempotencyStore,
    build_idempotency_key,
)
from pff_fa_ai.integration.execution.retry import execute_with_retry
from pff_fa_ai.integration.execution.states import IdempotencyStatus
from pff_fa_ai.integration.tools.models import ToolExecutionRequest, ToolResult, ToolResultError
from pff_fa_ai.integration.tools.registry import ToolRegistry
from pff_fa_ai.integration.tools.states import ToolCallStatus


class _ToolHttpError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


def _rejected(tool_id: str, reason: str) -> ToolResult:
    return ToolResult(
        tool_id=tool_id,
        status=ToolCallStatus.REJECTED,
        error=ToolResultError(
            code=IntegrationErrorCode.AUTHORIZATION_ERROR, message=reason, retryable=False
        ),
    )


def _classify_exception(exc: Exception) -> IntegrationErrorCode:
    if isinstance(exc, _ToolHttpError):
        return classify_http_status(exc.status_code)
    if isinstance(exc, httpx.TimeoutException):
        return IntegrationErrorCode.TIMEOUT
    if isinstance(exc, httpx.HTTPError):
        return IntegrationErrorCode.DEPENDENCY_ERROR
    return IntegrationErrorCode.UNKNOWN


class ToolExecutor:
    """doc 10 §32-34: the only controlled runtime path to enterprise capabilities."""

    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        api_catalog: ApiCatalog,
        http_client: EnterpriseHttpClient,
        retry_settings: RetrySettings,
        circuit_breaker_settings: CircuitBreakerSettings,
        concurrency_limiter: ConcurrencyLimiter,
        idempotency_store: IdempotencyStore | None = None,
    ) -> None:
        self._tools = tool_registry
        self._apis = api_catalog
        self._http = http_client
        self._retry_settings = retry_settings
        self._circuit_breaker_settings = circuit_breaker_settings
        self._concurrency = concurrency_limiter
        self._idempotency = idempotency_store or InMemoryIdempotencyStore()
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    async def execute(self, request: ToolExecutionRequest) -> ToolResult:
        # TOOL_REQUESTED -> TOOL_RESOLVED
        definition = self._tools.get(request.tool_id)
        if definition is None:
            return _rejected(request.tool_id, "Tool not registered")

        if not self._tools.is_agent_allowed(request.tool_id, request.agent_id):
            return _rejected(
                request.tool_id, f"Agent '{request.agent_id}' is not permitted to use this tool"
            )

        entry = self._apis.get(definition.source.api_id)
        if entry is None:
            return _rejected(
                request.tool_id, f"Tool references unknown api_id '{definition.source.api_id}'"
            )

        # AUTHORIZATION_CHECKED
        missing_claims = set(entry.authorization.claims) - set(request.claims.permissions)
        if missing_claims:
            return _rejected(request.tool_id, f"Missing required claims: {sorted(missing_claims)}")

        idempotency_key: str | None = None
        if definition.execution_policy.idempotent and entry.operation is ApiOperation.WRITE:
            idempotency_key = build_idempotency_key(
                workflow_instance_id=request.workflow_instance_id,
                operation_id=request.operation_id,
            )
            if await self._idempotency.get_status(idempotency_key) is IdempotencyStatus.COMPLETED:
                return ToolResult(tool_id=request.tool_id, status=ToolCallStatus.TOOL_COMPLETED)
            await self._idempotency.mark_in_progress(idempotency_key)

        breaker = self._circuit_breakers.setdefault(
            entry.api_id, CircuitBreaker(self._circuit_breaker_settings)
        )
        if not breaker.allow_request():
            if idempotency_key is not None:
                await self._idempotency.mark_failed(idempotency_key)
            return ToolResult(
                tool_id=request.tool_id,
                status=ToolCallStatus.REJECTED,
                error=ToolResultError(
                    code=IntegrationErrorCode.SERVICE_UNAVAILABLE,
                    message=f"Circuit open for api_id '{entry.api_id}'",
                    retryable=True,
                ),
            )

        # EXECUTING -> RESPONSE_RECEIVED -> RESPONSE_VALIDATED
        # doc 10 §72-74: the token APIM validated for this request is propagated
        # unchanged to the enterprise call, rather than the platform holding its own
        # per-API credential.
        propagated_headers = (
            {"Authorization": f"Bearer {request.claims.access_token}"}
            if request.claims.access_token
            else None
        )

        async def call() -> EnterpriseApiResponse:
            async with self._concurrency.acquire("enterprise"):
                response = await self._http.request(
                    entry=entry, path_params=request.arguments, headers=propagated_headers
                )
            if response.status_code >= 400:
                raise _ToolHttpError(response.status_code)
            return response

        try:
            response = await execute_with_retry(
                call,
                settings=self._retry_settings,
                should_retry=lambda exc: (
                    entry.execution.retryable and is_retryable(_classify_exception(exc))
                ),
            )
        except Exception as exc:
            breaker.record_failure()
            if idempotency_key is not None:
                await self._idempotency.mark_failed(idempotency_key)
            code = _classify_exception(exc)
            return ToolResult(
                tool_id=request.tool_id,
                status=ToolCallStatus.FAILED,
                error=ToolResultError(code=code, message=str(exc), retryable=is_retryable(code)),
            )

        breaker.record_success()

        # RESPONSE_TRANSFORMED -> TOOL_COMPLETED
        if idempotency_key is not None:
            await self._idempotency.mark_completed(idempotency_key)

        return ToolResult(
            tool_id=request.tool_id, status=ToolCallStatus.TOOL_COMPLETED, data=response.body
        )
