from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class PlatformError(Exception):
    def __init__(self, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = dict(details) if details else {}


class ValidationError(PlatformError):
    pass


class ConfigurationError(PlatformError):
    pass


class IntegrationError(PlatformError):
    pass


class ToolError(PlatformError):
    pass


class ModelError(PlatformError):
    pass


class RAGError(PlatformError):
    pass


class GuardrailError(PlatformError):
    pass


class WorkflowError(PlatformError):
    pass
