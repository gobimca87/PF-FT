from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_cache_configuration, load_memory_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_memory_configuration_from_the_real_config_repository() -> None:
    config = load_memory_configuration("dev")

    assert config.memory.default_ttl_seconds == 2592000
    assert config.memory.category_ttl_seconds["CONVERSATION"] == 2592000
    assert len(config.configuration_hash) == 64


def test_should_load_cache_configuration_from_the_real_config_repository() -> None:
    config = load_cache_configuration("dev")

    assert config.cache.default_ttl_seconds == 300
    assert config.cache.category_ttl_seconds["ENTERPRISE_API_RESPONSE"] == 300


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_memory_and_cache_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    memory_config = load_memory_configuration(environment)  # type: ignore[arg-type]
    cache_config = load_cache_configuration(environment)  # type: ignore[arg-type]

    assert memory_config.memory.default_ttl_seconds > 0
    assert cache_config.cache.default_ttl_seconds > 0


def test_should_fail_fast_when_memory_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "memory.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "memory.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_memory_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_memory_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "memory.yaml").write_text(
        "memory:\n  default_ttl_seconds: -1\n", encoding="utf-8"
    )
    (root / "environments" / "dev" / "memory.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid memory configuration"):
        load_memory_configuration("dev", config_root=root)


def test_should_fail_fast_when_cache_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "cache.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "cache.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_cache_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_cache_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "cache.yaml").write_text(
        "cache:\n  default_ttl_seconds: -1\n", encoding="utf-8"
    )
    (root / "environments" / "dev" / "cache.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid cache configuration"):
        load_cache_configuration("dev", config_root=root)
