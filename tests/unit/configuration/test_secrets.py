import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.secrets import EnvVarSecretResolver


def test_should_resolve_secret_from_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PF_FT_TEST_SECRET", "super-secret-value")

    resolved = EnvVarSecretResolver().resolve("PF_FT_TEST_SECRET")

    assert resolved == "super-secret-value"


def test_should_raise_configuration_error_when_secret_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PF_FT_UNSET_SECRET", raising=False)

    with pytest.raises(ConfigurationError, match="PF_FT_UNSET_SECRET"):
        EnvVarSecretResolver().resolve("PF_FT_UNSET_SECRET")
