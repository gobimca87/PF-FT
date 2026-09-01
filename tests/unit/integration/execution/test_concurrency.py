import asyncio

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.models import ConcurrencyPoolSettings, ConcurrencySettings
from pff_fa_ai.integration.execution.concurrency import ConcurrencyLimiter

SETTINGS = ConcurrencySettings(
    global_max=20,
    enterprise=ConcurrencyPoolSettings(max_parallel=2),
    mcp=ConcurrencyPoolSettings(max_parallel=1),
)


async def test_should_allow_calls_within_the_pool_limit() -> None:
    limiter = ConcurrencyLimiter(SETTINGS)

    async with limiter.acquire("enterprise"):
        pass  # no error


async def test_should_bound_concurrency_within_a_pool() -> None:
    limiter = ConcurrencyLimiter(SETTINGS)
    concurrent_count = 0
    max_observed = 0

    async def task() -> None:
        nonlocal concurrent_count, max_observed
        async with limiter.acquire("mcp"):
            concurrent_count += 1
            max_observed = max(max_observed, concurrent_count)
            await asyncio.sleep(0.01)
            concurrent_count -= 1

    await asyncio.gather(*(task() for _ in range(5)))

    assert max_observed <= SETTINGS.mcp.max_parallel


async def test_should_reject_an_unknown_pool_name() -> None:
    limiter = ConcurrencyLimiter(SETTINGS)

    with pytest.raises(ConfigurationError, match="Unknown concurrency pool"):
        async with limiter.acquire("unknown-pool"):
            pass
