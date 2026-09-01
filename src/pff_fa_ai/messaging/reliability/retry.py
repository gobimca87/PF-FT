from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

from pff_fa_ai.configuration.models import EventRetrySettings, RetrySettings
from pff_fa_ai.integration.errors.codes import IntegrationErrorCode, is_retryable
from pff_fa_ai.integration.execution.retry import execute_with_retry

ResultT = TypeVar("ResultT")

# doc 11 §74: only these categories are retry-eligible — the same stable classification
# doc 10 already defines for enterprise integrations (`IntegrationErrorCode`), reused
# here rather than duplicated. SCHEMA_ERROR/AUTHORIZATION_ERROR/BUSINESS_ERROR-equivalent
# codes are deliberately excluded from `is_retryable()`.


def _to_retry_settings(settings: EventRetrySettings) -> RetrySettings:
    return RetrySettings(
        max_attempts=settings.max_attempts,
        backoff="exponential",
        initial_ms=settings.initial_seconds * 1000,
        max_ms=settings.max_seconds * 1000,
        jitter=settings.jitter,
    )


async def execute_event_handler_with_retry(
    operation: Callable[[], Awaitable[ResultT]],
    *,
    settings: EventRetrySettings,
    classify: Callable[[Exception], IntegrationErrorCode],
) -> ResultT:
    """doc 11 §74-77: retries only eligible categories, bounded by `max_attempts`."""
    return await execute_with_retry(
        operation,
        settings=_to_retry_settings(settings),
        should_retry=lambda exc: is_retryable(classify(exc)),
    )
