from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from pf_ft_ai.configuration.models import RetrySettings

ResultT = TypeVar("ResultT")


def compute_backoff_delay_ms(attempt: int, *, settings: RetrySettings) -> float:
    """doc 10 §44: exponential backoff with full jitter."""
    exponential = settings.initial_ms * (2 ** (attempt - 1))
    capped = min(exponential, settings.max_ms)
    if settings.jitter:
        return random.uniform(0, capped)  # noqa: S311 -- retry jitter, not cryptographic
    return float(capped)


async def execute_with_retry(
    operation: Callable[[], Awaitable[ResultT]],
    *,
    settings: RetrySettings,
    should_retry: Callable[[Exception], bool],
) -> ResultT:
    """doc 10 §41-44: retry only retryable errors, bounded by max_attempts."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return await operation()
        except Exception as exc:
            if attempt >= settings.max_attempts or not should_retry(exc):
                raise
            await asyncio.sleep(compute_backoff_delay_ms(attempt, settings=settings) / 1000)
