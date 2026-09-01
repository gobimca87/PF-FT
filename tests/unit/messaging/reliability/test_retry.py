import pytest

from pff_fa_ai.common.exceptions import IntegrationError
from pff_fa_ai.configuration.models import EventRetrySettings
from pff_fa_ai.integration.errors.codes import IntegrationErrorCode
from pff_fa_ai.messaging.reliability.retry import execute_event_handler_with_retry

_SETTINGS = EventRetrySettings(max_attempts=2, initial_seconds=1, max_seconds=1, jitter=False)


def _classify(exc: Exception) -> IntegrationErrorCode:
    return (
        IntegrationErrorCode.SERVICE_UNAVAILABLE
        if isinstance(exc, IntegrationError)
        else (IntegrationErrorCode.VALIDATION_ERROR)
    )


async def test_should_succeed_without_retrying_when_the_first_attempt_works() -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        return "ok"

    result = await execute_event_handler_with_retry(
        operation, settings=_SETTINGS, classify=_classify
    )

    assert result == "ok"
    assert calls == 1


async def test_should_not_retry_a_non_retryable_error() -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        raise ValueError("permanent")

    with pytest.raises(ValueError, match="permanent"):
        await execute_event_handler_with_retry(operation, settings=_SETTINGS, classify=_classify)

    assert calls == 1


async def test_should_retry_a_retryable_error_up_to_max_attempts() -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        if calls < 2:
            raise IntegrationError("transient")
        return "recovered"

    result = await execute_event_handler_with_retry(
        operation, settings=_SETTINGS, classify=_classify
    )

    assert result == "recovered"
    assert calls == 2
