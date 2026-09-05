import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.secrets import (
    EnvVarSecretResolver,
    KeyVaultSecretResolver,
    SpnCredentials,
    build_key_vault_secret_resolver,
    secret_resolver_for_environment,
)

_SPN_ENV = {
    "AZURE_KEY_VAULT_URL": "https://kv.example.vault.azure.net/",
    "AZURE_TENANT_ID": "tenant-1",
    "AZURE_CLIENT_ID": "client-1",
    "AZURE_CLIENT_SECRET": "shh",  # pragma: allowlist secret -- fake test value
}


class _FakeKeyVaultClient:
    def __init__(self, secrets: dict[str, str]) -> None:
        self._secrets = secrets
        self.calls: list[str] = []

    def get_secret(self, name: str) -> str:
        self.calls.append(name)
        if name not in self._secrets:
            raise KeyError(name)
        return self._secrets[name]


def _spn() -> SpnCredentials:
    return SpnCredentials(tenant_id="t", client_id="c", client_secret="s")  # noqa: S106


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


def test_spn_credentials_from_environment_reads_all_three() -> None:
    creds = SpnCredentials.from_environment(_SPN_ENV)

    assert creds.tenant_id == "tenant-1"
    assert creds.client_id == "client-1"
    assert creds.client_secret == "shh"  # pragma: allowlist secret


def test_spn_credentials_fail_closed_when_any_value_missing() -> None:
    partial = dict(_SPN_ENV)
    del partial["AZURE_CLIENT_SECRET"]

    with pytest.raises(ConfigurationError, match="AZURE_CLIENT_SECRET"):
        SpnCredentials.from_environment(partial)


def test_spn_client_secret_is_not_rendered_in_repr() -> None:
    assert "shh" not in repr(SpnCredentials.from_environment(_SPN_ENV))


def test_key_vault_resolver_maps_underscore_refs_to_dash_names() -> None:
    client = _FakeKeyVaultClient({"AZURE-SERVICE-BUS-CONNECTION-STRING": "Endpoint=sb://..."})
    resolver = KeyVaultSecretResolver(vault_url="https://kv/", credentials=_spn(), client=client)

    assert resolver.resolve("AZURE_SERVICE_BUS_CONNECTION_STRING") == "Endpoint=sb://..."
    assert client.calls == ["AZURE-SERVICE-BUS-CONNECTION-STRING"]


def test_key_vault_resolver_caches_lookups() -> None:
    client = _FakeKeyVaultClient({"AZURE-REDIS-PASSWORD": "pw"})
    resolver = KeyVaultSecretResolver(vault_url="https://kv/", credentials=_spn(), client=client)

    resolver.resolve("AZURE_REDIS_PASSWORD")
    resolver.resolve("AZURE_REDIS_PASSWORD")

    assert client.calls == ["AZURE-REDIS-PASSWORD"]  # second call served from cache


def test_key_vault_resolver_wraps_backend_errors_as_configuration_error() -> None:
    resolver = KeyVaultSecretResolver(
        vault_url="https://kv/", credentials=_spn(), client=_FakeKeyVaultClient({})
    )

    with pytest.raises(ConfigurationError, match="Failed to resolve secret 'MISSING_ONE'"):
        resolver.resolve("MISSING_ONE")


def test_build_key_vault_resolver_requires_vault_url() -> None:
    env = {k: v for k, v in _SPN_ENV.items() if k != "AZURE_KEY_VAULT_URL"}

    with pytest.raises(ConfigurationError, match="AZURE_KEY_VAULT_URL"):
        build_key_vault_secret_resolver(env)


def test_selector_uses_key_vault_when_vault_url_present() -> None:
    resolver = secret_resolver_for_environment("dev", env=_SPN_ENV)

    assert isinstance(resolver, KeyVaultSecretResolver)


def test_selector_falls_back_to_env_for_local_dev_without_vault() -> None:
    resolver = secret_resolver_for_environment("dev", env={})

    assert isinstance(resolver, EnvVarSecretResolver)


def test_selector_fails_closed_for_prod_without_key_vault() -> None:
    with pytest.raises(ConfigurationError, match="must resolve secrets from Key Vault"):
        secret_resolver_for_environment("prod", env={})
