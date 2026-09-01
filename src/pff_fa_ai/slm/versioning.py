from __future__ import annotations

from pff_fa_ai.common.exceptions import ConfigurationError

_FLOATING_VERSION_TAGS = frozenset({"latest", ""})


def assert_pinned_model_version(model_version: str, *, environment: str) -> None:
    """Doc 15: production must pin an explicit model version, never 'latest'."""
    if environment == "prod" and model_version.strip().lower() in _FLOATING_VERSION_TAGS:
        raise ConfigurationError(
            f"Production SLM configuration must pin an explicit model version, got "
            f"'{model_version}'"
        )
