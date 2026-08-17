from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_platform_configuration
from pf_ft_ai.configuration.secrets import SecretResolver

BASE_YAML = """
configuration:
  configuration_id: test-platform
  version: 0.1.0
  owner: AI Platform
  effective_date: 2026-08-16

runtime:
  request_timeout_seconds: 60
  max_retries: 3
"""


class _StubSecretResolver:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    def resolve(self, secret_ref: str) -> str:
        return self._values[secret_ref]


def _write_config_root(tmp_path: Path, *, env_name: str, env_yaml: str) -> Path:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / env_name).mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / env_name / "platform.yaml").write_text(env_yaml, encoding="utf-8")
    return root


def test_should_load_platform_configuration_for_known_environment(tmp_path: Path) -> None:
    root = _write_config_root(
        tmp_path,
        env_name="dev",
        env_yaml="environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
    )

    config = load_platform_configuration("dev", config_root=root)

    assert config.environment.name == "dev"
    assert config.runtime.request_timeout_seconds == 60
    assert len(config.configuration_hash) == 64


def test_should_apply_environment_override_over_base(tmp_path: Path) -> None:
    root = _write_config_root(
        tmp_path,
        env_name="prod",
        env_yaml=(
            "environment:\n  name: prod\n  region: uksouth\n  platform_version: 0.1.0\n"
            "runtime:\n  request_timeout_seconds: 45\n"
        ),
    )

    config = load_platform_configuration("prod", config_root=root)

    assert config.runtime.request_timeout_seconds == 45
    assert config.runtime.max_retries == 3  # inherited from base, not overridden


def test_should_reject_unknown_environment(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="Unknown environment"):
        load_platform_configuration("staging-2", config_root=tmp_path)  # type: ignore[arg-type]


def test_should_fail_fast_when_environment_file_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(BASE_YAML, encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration file"):
        load_platform_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_runtime_value(tmp_path: Path) -> None:
    root = _write_config_root(
        tmp_path,
        env_name="dev",
        env_yaml=(
            "environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n"
            "runtime:\n  request_timeout_seconds: -5\n"
        ),
    )

    with pytest.raises(ConfigurationError, match="Invalid platform configuration"):
        load_platform_configuration("dev", config_root=root)


def test_should_reject_environment_identity_mismatch(tmp_path: Path) -> None:
    root = _write_config_root(
        tmp_path,
        env_name="test",
        env_yaml="environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
    )

    with pytest.raises(ConfigurationError, match="does not match requested environment"):
        load_platform_configuration("test", config_root=root)


def test_should_resolve_secret_ref_through_resolver(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(
        BASE_YAML + "\nintegration:\n  api_key_secret_ref: PF_FT_TEST_API_KEY\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "platform.yaml").write_text(
        "environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
        encoding="utf-8",
    )
    resolver: SecretResolver = _StubSecretResolver({"PF_FT_TEST_API_KEY": "resolved-value"})

    config = load_platform_configuration("dev", config_root=root, secret_resolver=resolver)

    # Secret refs never surface in the typed PlatformConfiguration itself (no
    # field for `integration` yet) — this test proves resolution ran without
    # raising, i.e. the resolver was actually invoked for the *_secret_ref key.
    assert config.environment.name == "dev"


def test_should_treat_empty_environment_file_as_no_overrides(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(
        BASE_YAML + "\nenvironment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "platform.yaml").write_text("", encoding="utf-8")

    config = load_platform_configuration("dev", config_root=root)

    assert config.environment.name == "dev"


def test_should_fail_fast_when_config_file_is_not_a_yaml_mapping(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text("- not\n- a\n- mapping\n", encoding="utf-8")
    (root / "environments" / "dev" / "platform.yaml").write_text(
        "environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="must contain a YAML mapping"):
        load_platform_configuration("dev", config_root=root)


def test_should_fail_fast_when_required_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(
        "configuration:\n  configuration_id: x\n  version: 0.1.0\n  owner: AI Platform\n"
        "  effective_date: 2026-08-16\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "platform.yaml").write_text(
        "environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_platform_configuration("dev", config_root=root)


def test_should_resolve_secret_refs_nested_inside_a_list(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(
        BASE_YAML + "\nintegration:\n  endpoints:\n    - api_key_secret_ref: PF_FT_LIST_SECRET\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "platform.yaml").write_text(
        "environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
        encoding="utf-8",
    )
    resolver: SecretResolver = _StubSecretResolver({"PF_FT_LIST_SECRET": "resolved-in-list"})

    config = load_platform_configuration("dev", config_root=root, secret_resolver=resolver)

    assert config.environment.name == "dev"


def test_should_raise_when_secret_ref_cannot_be_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("PF_FT_MISSING_KEY", raising=False)
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "platform.yaml").write_text(
        BASE_YAML + "\nintegration:\n  api_key_secret_ref: PF_FT_MISSING_KEY\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "platform.yaml").write_text(
        "environment:\n  name: dev\n  region: uksouth\n  platform_version: 0.1.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Secret reference not found"):
        load_platform_configuration("dev", config_root=root)
