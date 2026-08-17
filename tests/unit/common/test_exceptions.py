import pytest

from pf_ft_ai.common.exceptions import ConfigurationError, PlatformError


def test_should_carry_message_and_details() -> None:
    error = ConfigurationError("bad config", details={"field": "runtime.max_retries"})

    assert error.message == "bad config"
    assert error.details == {"field": "runtime.max_retries"}


def test_should_be_a_platform_error() -> None:
    with pytest.raises(PlatformError):
        raise ConfigurationError("bad config")
