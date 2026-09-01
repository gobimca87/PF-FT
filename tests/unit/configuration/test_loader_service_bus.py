from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_service_bus_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


class _StubResolver:
    def resolve(self, secret_ref: str) -> str:
        assert secret_ref == "AZURE_SERVICE_BUS_CONNECTION_STRING"
        return "Endpoint=sb://pff-fa-example.servicebus.windows.net/;SharedAccessKeyName=x;SharedAccessKey=y"


def test_should_load_service_bus_configuration_from_the_real_config_repository() -> None:
    config = load_service_bus_configuration("dev", secret_resolver=_StubResolver())

    assert config.topic.name == "pff-fa-enterprise-events-dev"
    assert config.topic.subscription_name == "pff-fa-ai-runtime-dev"
    assert "HIL_TASK_COMPLETED" in config.topic.event_type_filters
    assert config.connection.connection_string.startswith("Endpoint=")
    assert config.consumer.max_concurrent_messages == 10
    assert config.retry.max_attempts == 5
    assert config.retry.initial_seconds == 2
    assert config.retry.max_seconds == 60
    assert config.retry.jitter is True


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_a_distinct_topic_name_per_environment(environment: str) -> None:
    config = load_service_bus_configuration(environment, secret_resolver=_StubResolver())  # type: ignore[arg-type]

    assert config.topic.name == f"pff-fa-enterprise-events-{environment}"
    assert config.topic.subscription_name == f"pff-fa-ai-runtime-{environment}"
    assert config.topic.description
    assert config.topic.subscription_description


def test_should_raise_when_the_connection_secret_is_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AZURE_SERVICE_BUS_CONNECTION_STRING", raising=False)

    with pytest.raises(ConfigurationError, match="Secret reference not found"):
        load_service_bus_configuration("dev")


def test_should_fail_fast_when_topic_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "service-bus.yaml").write_text(
        "connection:\n  connection_string_secret_ref: AZURE_SERVICE_BUS_CONNECTION_STRING\n"
        "consumer:\n  max_concurrent_messages: 10\n  processing_timeout_seconds: 60\n"
        "retry:\n  max_attempts: 5\n  initial_seconds: 2\n  max_seconds: 60\n  jitter: true\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "service-bus.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_service_bus_configuration("dev", config_root=root, secret_resolver=_StubResolver())
