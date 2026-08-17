from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import CONFIG_ROOT
from pf_ft_ai.configuration.models import ReleaseManifest


def load_release_manifest(version: str, *, config_root: Path | None = None) -> ReleaseManifest:
    root = config_root or CONFIG_ROOT
    path = root / "releases" / f"{version}.yaml"
    if not path.is_file():
        raise ConfigurationError(f"Release manifest not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict) or "release" not in raw:
        raise ConfigurationError(f"Release manifest missing top-level 'release' key: {path}")

    try:
        return ReleaseManifest.model_validate(raw["release"])
    except PydanticValidationError as exc:
        raise ConfigurationError(f"Invalid release manifest: {exc}") from exc
