from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.common.validation import format_validation_error
from pf_ft_ai.configuration.loader import resolve_secret_refs
from pf_ft_ai.configuration.secrets import EnvVarSecretResolver, SecretResolver


class ApiOperation(StrEnum):
    READ = "READ"
    WRITE = "WRITE"


class ApiEndpoint(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str


class ApiAuthorization(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    required: bool = True
    claims: tuple[str, ...] = Field(default_factory=tuple)


class ApiExecutionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    idempotent: bool
    retryable: bool
    parallelizable: bool
    max_parallelism: int | None = Field(default=None, gt=0)


class ApiCatalogEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    api_id: str
    name: str
    version: str
    owner: str
    domain: str
    operation: ApiOperation
    endpoint: ApiEndpoint
    authorization: ApiAuthorization
    execution: ApiExecutionPolicy


class ApiCatalog:
    def __init__(self, entries: Iterable[ApiCatalogEntry] = ()) -> None:
        self._entries: dict[str, ApiCatalogEntry] = {}
        for entry in entries:
            self.register(entry)

    def register(self, entry: ApiCatalogEntry) -> None:
        """doc 10 §129: API IDs must be unique in the catalog."""
        if entry.api_id in self._entries:
            raise ConfigurationError(f"Duplicate api_id in catalog: {entry.api_id}")
        self._entries[entry.api_id] = entry

    def get(self, api_id: str) -> ApiCatalogEntry | None:
        return self._entries.get(api_id)

    def __len__(self) -> int:
        return len(self._entries)


def load_api_catalog(
    directory: Path, *, secret_resolver: SecretResolver | None = None
) -> ApiCatalog:
    """doc 10 §7, §123: one YAML file per domain; `*_secret_ref` keys are resolved the same
    way as every other configuration category."""
    catalog = ApiCatalog()
    if not directory.is_dir():
        return catalog

    resolver = secret_resolver or EnvVarSecretResolver()
    for path in sorted(directory.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not raw:
            continue
        entries = raw if isinstance(raw, list) else [raw]
        for entry_data in entries:
            resolved = resolve_secret_refs(entry_data, resolver)
            try:
                entry = ApiCatalogEntry.model_validate(resolved)
            except PydanticValidationError as exc:
                raise ConfigurationError(
                    f"Invalid API catalog entry in {path}: {format_validation_error(exc)}"
                ) from exc
            catalog.register(entry)

    return catalog
