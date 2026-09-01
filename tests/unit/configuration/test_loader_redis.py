from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_redis_configuration

BASE_YAML = """
redis:
  host: localhost
  port: 6379
  ssl: false
  db: 0
"""


def test_should_load_redis_configuration_for_a_synthetic_repository(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "redis.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "redis.yaml").write_text("", encoding="utf-8")

    config = load_redis_configuration("dev", config_root=root)

    assert config.redis.host == "localhost"
    assert config.redis.port == 6379
    assert config.redis.password is None
    assert len(config.configuration_hash) == 64


def test_should_resolve_password_secret_ref(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "prod").mkdir(parents=True)
    (root / "base" / "redis.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "prod" / "redis.yaml").write_text(
        "redis:\n  host: prod-redis.example\n  ssl: true\n"
        "  password_secret_ref: AZURE_REDIS_PASSWORD\n",
        encoding="utf-8",
    )

    class _StubResolver:
        def resolve(self, secret_ref: str) -> str:
            assert secret_ref == "AZURE_REDIS_PASSWORD"
            return "super-secret"

    config = load_redis_configuration("prod", config_root=root, secret_resolver=_StubResolver())

    assert config.redis.host == "prod-redis.example"
    assert config.redis.ssl is True
    assert config.redis.password == "super-secret"


def test_should_fail_fast_when_redis_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "redis.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "redis.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_redis_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_redis_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "redis.yaml").write_text(
        BASE_YAML.replace("port: 6379", "port: -1"), encoding="utf-8"
    )
    (root / "environments" / "dev" / "redis.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid redis configuration"):
        load_redis_configuration("dev", config_root=root)


def test_should_load_dev_test_and_uat_from_the_real_config_repository() -> None:
    for environment in ("dev", "test", "uat"):
        config = load_redis_configuration(environment)
        assert config.redis.host == "localhost"
        assert config.redis.ssl is False


def test_should_fail_fast_for_staging_and_prod_placeholders_without_the_real_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AZURE_REDIS_PASSWORD", raising=False)
    for environment in ("staging", "prod"):
        with pytest.raises(ConfigurationError, match="Secret reference not found"):
            load_redis_configuration(environment)
