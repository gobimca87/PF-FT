from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.models import Environment

# ADR-D5-07 / ADR-D5-20: the Key Vault connection is established ONLY from the enterprise
# service-principal (MI-SPN) — tenant id, client id and client secret. No other credential
# method is used (no DefaultAzureCredential, no CLI/VS/interactive credential, no managed
# identity without an explicit SPN). The Azure CI/CD pipeline variable group holds the SPN
# values and injects them into the workload's environment; this module reads them there.
KEY_VAULT_URL_ENV = "AZURE_KEY_VAULT_URL"
SPN_TENANT_ID_ENV = "AZURE_TENANT_ID"
SPN_CLIENT_ID_ENV = "AZURE_CLIENT_ID"
SPN_CLIENT_SECRET_ENV = "AZURE_CLIENT_SECRET"  # noqa: S105  # pragma: allowlist secret

# Azure Key Vault secret names allow only alphanumerics and dashes; the `*_secret_ref`
# values in config use UPPER_SNAKE_CASE, so underscores are translated to dashes.
_KV_SECRET_NAME = re.compile(r"^[0-9a-zA-Z-]+$")

# Environments that must never fall back to a non-Key-Vault secret source: a deployed
# runtime resolves every secret from Key Vault via the SPN, fail-closed.
_DEPLOYED_ENVIRONMENTS: frozenset[Environment] = frozenset({"uat", "staging", "prod"})


class SecretResolver(Protocol):
    def resolve(self, secret_ref: str) -> str: ...


class EnvVarSecretResolver:
    """Local/dev-only resolver — reads secrets straight from the process environment. It is
    never used in a deployed environment (see `secret_resolver_for_environment`), where the
    SPN-backed Key Vault resolver is mandatory."""

    def resolve(self, secret_ref: str) -> str:
        value = os.environ.get(secret_ref)
        if value is None:
            raise ConfigurationError(f"Secret reference not found in environment: {secret_ref}")
        return value


class SpnCredentials(BaseModel):
    """The enterprise service-principal used to authenticate to Key Vault (ADR-D5-07).
    `client_secret` is never rendered (`repr=False`)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str = Field(min_length=1)
    client_id: str = Field(min_length=1)
    client_secret: str = Field(min_length=1, repr=False)

    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> SpnCredentials:
        source = os.environ if env is None else env
        values = {
            "tenant_id": source.get(SPN_TENANT_ID_ENV, ""),
            "client_id": source.get(SPN_CLIENT_ID_ENV, ""),
            "client_secret": source.get(SPN_CLIENT_SECRET_ENV, ""),
        }
        missing = [
            env_name
            for env_name, field_name in (
                (SPN_TENANT_ID_ENV, "tenant_id"),
                (SPN_CLIENT_ID_ENV, "client_id"),
                (SPN_CLIENT_SECRET_ENV, "client_secret"),
            )
            if not values[field_name]
        ]
        if missing:
            raise ConfigurationError(
                "Key Vault requires the service-principal credentials "
                f"{', '.join(sorted(missing))} — set them from the Azure CI/CD pipeline "
                "variable group; no other authentication method is permitted"
            )
        return cls(**values)


def _to_key_vault_secret_name(secret_ref: str) -> str:
    name = secret_ref.replace("_", "-")
    if not _KV_SECRET_NAME.match(name):
        raise ConfigurationError(
            f"Secret reference '{secret_ref}' does not map to a valid Key Vault secret name "
            f"('{name}'); use letters, digits and underscores only"
        )
    return name


class KeyVaultSecretClient(Protocol):
    """Minimal seam over the Azure Key Vault secrets client so the resolver is unit-testable
    without a live vault; production uses `AzureKeyVaultSecretClient`."""

    def get_secret(self, name: str) -> str: ...


class AzureKeyVaultSecretClient:
    """The only supported Key Vault client. Authenticates with a `ClientSecretCredential`
    built from the SPN (tenant/client id + client secret) and nothing else (ADR-D5-07,
    ADR-D5-20). The Azure SDK is imported lazily so the module stays importable — and
    unit-testable through the `KeyVaultSecretClient` seam — without the SDK installed."""

    def __init__(self, *, vault_url: str, credentials: SpnCredentials) -> None:
        from azure.identity import ClientSecretCredential
        from azure.keyvault.secrets import SecretClient

        credential = ClientSecretCredential(
            tenant_id=credentials.tenant_id,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
        )
        self._client = SecretClient(vault_url=vault_url, credential=credential)

    def get_secret(self, name: str) -> str:
        secret = self._client.get_secret(name)
        value = secret.value
        if value is None:
            raise ConfigurationError(f"Key Vault secret '{name}' has no value")
        return value


class KeyVaultSecretResolver:
    """Resolves `*_secret_ref` config references from Azure Key Vault. The connection is
    established ONLY via the SPN (`SpnCredentials`); no other authentication method is
    permitted (ADR-D5-07 / ADR-D5-20). Results are cached for the process lifetime."""

    def __init__(
        self,
        *,
        vault_url: str,
        credentials: SpnCredentials,
        client: KeyVaultSecretClient | None = None,
    ) -> None:
        if not vault_url:
            raise ConfigurationError(
                f"Key Vault URL is required (set {KEY_VAULT_URL_ENV}) — the secret store "
                "cannot be reached without it"
            )
        self._vault_url = vault_url
        self._credentials = credentials
        self._client = client
        self._cache: dict[str, str] = {}

    def _get_client(self) -> KeyVaultSecretClient:
        if self._client is None:
            self._client = AzureKeyVaultSecretClient(
                vault_url=self._vault_url, credentials=self._credentials
            )
        return self._client

    def resolve(self, secret_ref: str) -> str:
        name = _to_key_vault_secret_name(secret_ref)
        if name in self._cache:
            return self._cache[name]
        try:
            value = self._get_client().get_secret(name)
        except ConfigurationError:
            raise
        except Exception as exc:  # noqa: BLE001 -- surface any SDK/transport error uniformly
            raise ConfigurationError(
                f"Failed to resolve secret '{secret_ref}' (Key Vault name '{name}') from "
                f"{self._vault_url}"
            ) from exc
        self._cache[name] = value
        return value


def build_key_vault_secret_resolver(
    env: Mapping[str, str] | None = None,
) -> KeyVaultSecretResolver:
    """Construct the SPN-backed Key Vault resolver from the environment (the Azure CI/CD
    pipeline variable group populates these). Fails closed if the vault URL or any SPN
    credential is missing."""
    source = os.environ if env is None else env
    vault_url = source.get(KEY_VAULT_URL_ENV, "")
    if not vault_url:
        raise ConfigurationError(
            f"{KEY_VAULT_URL_ENV} is not set — a deployed runtime resolves every secret from "
            "Key Vault via the service principal and cannot start without the vault URL"
        )
    return KeyVaultSecretResolver(
        vault_url=vault_url, credentials=SpnCredentials.from_environment(source)
    )


def secret_resolver_for_environment(
    environment: Environment, *, env: Mapping[str, str] | None = None
) -> SecretResolver:
    """Select the secret resolver for the running environment.

    Deployed environments (uat/staging/prod) MUST resolve secrets from Key Vault via the
    SPN — fail-closed, no other method. Local environments (dev/test) use Key Vault too when
    a vault URL is configured, otherwise fall back to the process environment for developer
    convenience."""
    source = os.environ if env is None else env
    if source.get(KEY_VAULT_URL_ENV):
        return build_key_vault_secret_resolver(source)
    if environment in _DEPLOYED_ENVIRONMENTS:
        raise ConfigurationError(
            f"Environment '{environment}' must resolve secrets from Key Vault via the "
            f"service principal, but {KEY_VAULT_URL_ENV} and the SPN credentials are not set"
        )
    return EnvVarSecretResolver()
