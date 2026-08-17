import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.slm.versioning import assert_pinned_model_version


def test_should_reject_latest_in_production() -> None:
    with pytest.raises(ConfigurationError, match="must pin an explicit model version"):
        assert_pinned_model_version("latest", environment="prod")


def test_should_accept_an_explicit_version_in_production() -> None:
    assert_pinned_model_version("1.2.0", environment="prod")


def test_should_allow_latest_outside_production() -> None:
    assert_pinned_model_version("latest", environment="dev")
