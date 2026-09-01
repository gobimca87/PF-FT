from redis.asyncio import Redis

from pff_fa_ai.configuration.models import RedisConnectionSettings
from pff_fa_ai.infrastructure.redis_client import build_redis_client


def test_should_build_a_redis_client_from_connection_settings() -> None:
    settings = RedisConnectionSettings(
        host="pff-fa-redis.example", port=10000, ssl=True, db=0, password="super-secret"
    )

    client = build_redis_client(settings)

    assert isinstance(client, Redis)
    connection_kwargs = client.connection_pool.connection_kwargs
    assert connection_kwargs["host"] == "pff-fa-redis.example"
    assert connection_kwargs["port"] == 10000
    assert connection_kwargs["db"] == 0
    assert connection_kwargs["password"] == "super-secret"
