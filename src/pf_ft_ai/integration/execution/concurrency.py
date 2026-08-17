from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.models import ConcurrencySettings


class ConcurrencyLimiter:
    """doc 10 §55, §91-92: bounded parallelism with per-pool bulkhead isolation."""

    def __init__(self, settings: ConcurrencySettings) -> None:
        self._global = asyncio.Semaphore(settings.global_max)
        self._pools = {
            "enterprise": asyncio.Semaphore(settings.enterprise.max_parallel),
            "mcp": asyncio.Semaphore(settings.mcp.max_parallel),
        }

    @asynccontextmanager
    async def acquire(self, pool: str) -> AsyncIterator[None]:
        if pool not in self._pools:
            raise ConfigurationError(f"Unknown concurrency pool: {pool}")
        async with self._global, self._pools[pool]:
            yield
