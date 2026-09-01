import pytest

from pff_fa_ai.configuration.models import RetrySettings
from pff_fa_ai.integration.execution.retry import compute_backoff_delay_ms, execute_with_retry

SETTINGS_NO_JITTER = RetrySettings(
    max_attempts=3, backoff="exponential", initial_ms=250, max_ms=5000, jitter=False
)
SETTINGS_JITTER = RetrySettings(
    max_attempts=3, backoff="exponential", initial_ms=250, max_ms=5000, jitter=True
)


def test_backoff_should_grow_exponentially_without_jitter() -> None:
    assert compute_backoff_delay_ms(1, settings=SETTINGS_NO_JITTER) == 250
    assert compute_backoff_delay_ms(2, settings=SETTINGS_NO_JITTER) == 500
    assert compute_backoff_delay_ms(3, settings=SETTINGS_NO_JITTER) == 1000


def test_backoff_should_cap_at_max_ms() -> None:
    assert compute_backoff_delay_ms(10, settings=SETTINGS_NO_JITTER) == 5000


def test_backoff_with_jitter_should_stay_within_bounds() -> None:
    delay = compute_backoff_delay_ms(2, settings=SETTINGS_JITTER)

    assert 0 <= delay <= 500


async def test_should_return_result_on_first_success_without_retrying() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        return "ok"

    result = await execute_with_retry(
        operation, settings=SETTINGS_NO_JITTER, should_retry=lambda exc: True
    )

    assert result == "ok"
    assert attempts == 1


async def test_should_retry_a_retryable_failure_then_succeed() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise TimeoutError("transient")
        return "recovered"

    result = await execute_with_retry(
        operation, settings=SETTINGS_NO_JITTER, should_retry=lambda exc: True
    )

    assert result == "recovered"
    assert attempts == 2


async def test_should_stop_retrying_once_max_attempts_reached() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise TimeoutError("always fails")

    with pytest.raises(TimeoutError):
        await execute_with_retry(
            operation, settings=SETTINGS_NO_JITTER, should_retry=lambda exc: True
        )

    assert attempts == SETTINGS_NO_JITTER.max_attempts


async def test_should_not_retry_when_error_is_not_retryable() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise ValueError("non-retryable")

    with pytest.raises(ValueError, match="non-retryable"):
        await execute_with_retry(
            operation, settings=SETTINGS_NO_JITTER, should_retry=lambda exc: False
        )

    assert attempts == 1
