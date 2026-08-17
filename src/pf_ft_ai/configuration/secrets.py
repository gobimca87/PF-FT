from __future__ import annotations

import os
from typing import Protocol

from pf_ft_ai.common.exceptions import ConfigurationError


class SecretResolver(Protocol):
    def resolve(self, secret_ref: str) -> str: ...


class EnvVarSecretResolver:
    def resolve(self, secret_ref: str) -> str:
        value = os.environ.get(secret_ref)
        if value is None:
            raise ConfigurationError(f"Secret reference not found in environment: {secret_ref}")
        return value
