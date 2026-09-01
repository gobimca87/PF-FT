from __future__ import annotations

from redis.asyncio import Redis

from pff_fa_ai.configuration.models import RedisConnectionSettings


def build_redis_client(settings: RedisConnectionSettings) -> Redis:
    """Azure Managed Redis is RESP-protocol-compatible (docs/adr/0004) — plain redis-py works."""
    return Redis(
        host=settings.host,
        port=settings.port,
        db=settings.db,
        ssl=settings.ssl,
        password=settings.password,
        decode_responses=True,
    )
