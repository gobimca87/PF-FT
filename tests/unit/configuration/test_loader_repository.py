import pytest

from pff_fa_ai.configuration.loader import load_platform_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_platform_configuration(environment)  # type: ignore[arg-type]

    assert config.environment.name == environment
    assert config.metadata.configuration_id == "pff-fa-ai-platform"


def test_should_apply_prod_runtime_timeout_override_from_real_repository() -> None:
    config = load_platform_configuration("prod")

    assert config.runtime.request_timeout_seconds == 45
