import pytest
from fastapi import FastAPI

from pff_fa_ai.api.main import _ENVIRONMENT_VAR, _environment_from_env, app
from pff_fa_ai.common.exceptions import ConfigurationError


def test_should_default_to_dev_when_the_environment_variable_is_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(_ENVIRONMENT_VAR, raising=False)

    assert _environment_from_env() == "dev"


def test_should_read_a_valid_environment_from_the_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(_ENVIRONMENT_VAR, "prod")

    assert _environment_from_env() == "prod"


def test_should_reject_an_unknown_environment_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_ENVIRONMENT_VAR, "not-a-real-environment")

    with pytest.raises(ConfigurationError, match="is not one of"):
        _environment_from_env()


def test_module_level_app_should_be_a_ready_fastapi_instance() -> None:
    assert isinstance(app, FastAPI)
