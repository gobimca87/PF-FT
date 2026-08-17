from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_conversation_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS

BASE_YAML = """
conversation:
  max_history_messages: 50
  max_history_tokens: 12000
  summary_threshold_tokens: 10000
  max_message_size: 10000

session:
  idle_timeout_minutes: 30
  absolute_timeout_hours: 8

security:
  enforce_ownership: true
  enforce_tenant_isolation: true

workflow:
  resume_enabled: true
"""


def test_should_load_conversation_configuration_for_a_synthetic_repository(
    tmp_path: Path,
) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "conversation.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "conversation.yaml").write_text("", encoding="utf-8")

    config = load_conversation_configuration("dev", config_root=root)

    assert config.session.idle_timeout_minutes == 30
    assert config.session.absolute_timeout_hours == 8
    assert config.workflow.resume_enabled is True


def test_should_fail_fast_on_invalid_conversation_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "conversation.yaml").write_text(
        BASE_YAML.replace("idle_timeout_minutes: 30", "idle_timeout_minutes: -1"),
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "conversation.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid conversation configuration"):
        load_conversation_configuration("dev", config_root=root)


def test_should_fail_fast_when_conversation_config_missing_section(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "conversation.yaml").write_text(
        "conversation:\n  max_history_messages: 50\n"
        "  max_history_tokens: 12000\n  summary_threshold_tokens: 10000\n"
        "  max_message_size: 10000\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "conversation.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_conversation_configuration("dev", config_root=root)


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_conversation_configuration(environment)  # type: ignore[arg-type]

    assert config.session.idle_timeout_minutes == 30
