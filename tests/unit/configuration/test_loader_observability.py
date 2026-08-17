from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_observability_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_observability_configuration_from_the_real_config_repository() -> None:
    config = load_observability_configuration("dev")

    assert config.langfuse.enabled is False
    assert config.langfuse.host is None
    assert config.circuit_breaker.failure_threshold == 5


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_observability_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_observability_configuration(environment)  # type: ignore[arg-type]

    assert config.langfuse.enabled is False


def test_should_fail_fast_when_langfuse_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "observability.yaml").write_text(
        "circuit_breaker:\n  failure_threshold: 5\n  cooldown_seconds: 30\n"
        "  half_open_max_calls: 1\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "observability.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_observability_configuration("dev", config_root=root)


def test_should_resolve_langfuse_secret_refs_when_enabled(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "observability.yaml").write_text(
        "langfuse:\n  enabled: true\n  host_secret_ref: TEST_LANGFUSE_HOST\n"
        "  public_key_secret_ref: TEST_LANGFUSE_PUBLIC_KEY\n"
        "  secret_key_secret_ref: TEST_LANGFUSE_SECRET_KEY\n"
        "circuit_breaker:\n  failure_threshold: 5\n  cooldown_seconds: 30\n"
        "  half_open_max_calls: 1\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "observability.yaml").write_text("", encoding="utf-8")

    class _StubResolver:
        def resolve(self, secret_ref: str) -> str:
            return {
                "TEST_LANGFUSE_HOST": "https://cloud.langfuse.com",
                "TEST_LANGFUSE_PUBLIC_KEY": "pk-test",
                "TEST_LANGFUSE_SECRET_KEY": "sk-test",
            }[secret_ref]

    config = load_observability_configuration(
        "dev", config_root=root, secret_resolver=_StubResolver()
    )

    assert config.langfuse.enabled is True
    assert config.langfuse.host == "https://cloud.langfuse.com"
    assert config.langfuse.public_key == "pk-test"
    assert config.langfuse.secret_key == "sk-test"
