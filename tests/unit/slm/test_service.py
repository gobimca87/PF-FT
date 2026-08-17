from collections.abc import AsyncIterator

import pytest

from pf_ft_ai.common.exceptions import IntegrationError, ModelError
from pf_ft_ai.configuration.models import CircuitBreakerSettings, RetrySettings
from pf_ft_ai.slm.models import SlmMessage, SlmRequest, SlmResponse, SlmUsage
from pf_ft_ai.slm.providers import MockSLMProvider
from pf_ft_ai.slm.service import SlmService, _is_transient
from pf_ft_ai.slm.states import ProviderHealthStatus, SlmStatus

_RETRY = RetrySettings(max_attempts=3, backoff="exponential", initial_ms=1, max_ms=5, jitter=False)
_CIRCUIT = CircuitBreakerSettings(failure_threshold=2, cooldown_seconds=60, half_open_max_calls=1)


def _request() -> SlmRequest:
    return SlmRequest(
        model_id="mock-slm-v1",
        messages=(SlmMessage(role="user", content="Hello"),),
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=64,
    )


def _response() -> SlmResponse:
    return SlmResponse(
        request_id="req-1",
        model_id="mock-slm-v1",
        model_version="1.0.0",
        output="hello back",
        usage=SlmUsage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        finish_reason="stop",
    )


class _FailingProvider:
    def __init__(self, *, status_code: int, fail_times: int) -> None:
        self._status_code = status_code
        self._fail_times = fail_times
        self.calls = 0

    async def generate(self, request: SlmRequest) -> SlmResponse:
        self.calls += 1
        if self.calls <= self._fail_times:
            raise IntegrationError("transient failure", details={"status_code": self._status_code})
        return _response()

    def stream(self, request: SlmRequest) -> AsyncIterator[str]:
        raise NotImplementedError

    async def health(self) -> ProviderHealthStatus:
        return ProviderHealthStatus.UNAVAILABLE


def test_is_transient_should_be_false_for_non_integration_errors() -> None:
    assert _is_transient(ValueError("not an integration error")) is False


async def test_should_succeed_on_the_first_attempt() -> None:
    provider = _FailingProvider(status_code=503, fail_times=0)
    service = SlmService(provider, retry=_RETRY, circuit_breaker=_CIRCUIT)

    result = await service.generate(_request())

    assert result.status is SlmStatus.SUCCEEDED
    assert provider.calls == 1


async def test_should_retry_transient_failures_and_then_succeed() -> None:
    provider = _FailingProvider(status_code=503, fail_times=2)
    service = SlmService(provider, retry=_RETRY, circuit_breaker=_CIRCUIT)

    result = await service.generate(_request())

    assert result.status is SlmStatus.SUCCEEDED
    assert provider.calls == 3


async def test_should_not_retry_non_transient_failures() -> None:
    provider = _FailingProvider(status_code=400, fail_times=5)
    service = SlmService(provider, retry=_RETRY, circuit_breaker=_CIRCUIT)

    with pytest.raises(ModelError):
        await service.generate(_request())

    assert provider.calls == 1


async def test_should_fall_back_when_primary_fails_after_retries_are_exhausted() -> None:
    provider = _FailingProvider(status_code=503, fail_times=10)
    fallback = MockSLMProvider()
    service = SlmService(provider, retry=_RETRY, circuit_breaker=_CIRCUIT, fallback=fallback)

    result = await service.generate(_request())

    assert result.status is SlmStatus.FALLBACK


async def test_should_raise_when_primary_fails_and_no_fallback_is_configured() -> None:
    provider = _FailingProvider(status_code=503, fail_times=10)
    service = SlmService(provider, retry=_RETRY, circuit_breaker=_CIRCUIT)

    with pytest.raises(ModelError, match="no fallback model"):
        await service.generate(_request())


async def test_should_open_the_circuit_after_repeated_failures_and_use_fallback() -> None:
    provider = _FailingProvider(status_code=503, fail_times=100)
    fallback = MockSLMProvider()
    single_attempt_retry = RetrySettings(
        max_attempts=1, backoff="exponential", initial_ms=1, max_ms=5, jitter=False
    )
    service = SlmService(
        provider, retry=single_attempt_retry, circuit_breaker=_CIRCUIT, fallback=fallback
    )

    await service.generate(_request())
    await service.generate(_request())
    calls_before_circuit_opens = provider.calls

    result = await service.generate(_request())

    assert result.status is SlmStatus.FALLBACK
    # doc 10 §90 circuit semantics reused for SLM: once OPEN, the primary is not called.
    assert provider.calls == calls_before_circuit_opens
