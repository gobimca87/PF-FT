from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pf_ft_ai.common.exceptions import IntegrationError, ModelError
from pf_ft_ai.configuration.models import CircuitBreakerSettings, RetrySettings
from pf_ft_ai.integration.execution.circuit import CircuitBreaker
from pf_ft_ai.integration.execution.retry import execute_with_retry
from pf_ft_ai.slm.models import SlmRequest, SlmResponse
from pf_ft_ai.slm.providers import SLMProvider
from pf_ft_ai.slm.states import SlmStatus

_TRANSIENT_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def _is_transient(exc: Exception) -> bool:
    if isinstance(exc, IntegrationError):
        return exc.details.get("status_code") in _TRANSIENT_STATUS_CODES
    return False


class SlmExecutionResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    response: SlmResponse
    status: SlmStatus


class SlmService:
    """Doc 15 / DEVELOPMENT-GUIDE Phase 9 reliability: retry only transient errors with
    backoff+jitter; circuit breaker; fallback to an approved model — never silent (the
    caller always learns whether the primary or the fallback served the response via
    `SlmExecutionResult.status`). Retry/circuit-breaker algorithms are the same generic
    primitives doc 10 defines for enterprise integrations — reused here rather than
    duplicated.
    """

    def __init__(
        self,
        primary: SLMProvider,
        *,
        retry: RetrySettings,
        circuit_breaker: CircuitBreakerSettings,
        fallback: SLMProvider | None = None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._retry = retry
        self._circuit = CircuitBreaker(circuit_breaker)

    async def generate(self, request: SlmRequest) -> SlmExecutionResult:
        if not self._circuit.allow_request():
            return await self._fallback_or_raise(
                request, ModelError("SLM circuit breaker is open for the primary provider")
            )

        try:
            response = await execute_with_retry(
                lambda: self._primary.generate(request),
                settings=self._retry,
                should_retry=_is_transient,
            )
        except Exception as exc:
            self._circuit.record_failure()
            return await self._fallback_or_raise(request, exc)

        self._circuit.record_success()
        return SlmExecutionResult(response=response, status=SlmStatus.SUCCEEDED)

    async def _fallback_or_raise(self, request: SlmRequest, cause: Exception) -> SlmExecutionResult:
        if self._fallback is None:
            raise ModelError(
                "SLM primary provider failed and no fallback model is configured"
            ) from cause
        response = await self._fallback.generate(request)
        return SlmExecutionResult(response=response, status=SlmStatus.FALLBACK)
