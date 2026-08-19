from __future__ import annotations

import os

from fastapi import FastAPI

from pf_ft_ai.api.app import create_app
from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS, Environment

_ENVIRONMENT_VAR = "PFFT_ENVIRONMENT"


def _environment_from_env() -> Environment:
    """doc 25 (Infrastructure) / DEVELOPMENT-GUIDE Phase 19: the container entrypoint —
    `create_app()` itself stays a pure factory (Phase 3) that never reads process
    environment directly; only this thin wiring layer, used by the ASGI server, does."""
    raw = os.environ.get(_ENVIRONMENT_VAR, "dev")
    if raw not in ALLOWED_ENVIRONMENTS:
        raise ConfigurationError(f"{_ENVIRONMENT_VAR}='{raw}' is not one of {ALLOWED_ENVIRONMENTS}")
    return raw


app: FastAPI = create_app(environment=_environment_from_env())
