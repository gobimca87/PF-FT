from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any


def compute_configuration_hash(configuration: Mapping[str, Any]) -> str:
    canonical = json.dumps(configuration, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
