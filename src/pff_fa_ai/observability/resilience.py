from __future__ import annotations

from enum import StrEnum

from pff_fa_ai.configuration.models import CircuitBreakerSettings
from pff_fa_ai.integration.execution.circuit import CircuitBreaker


class ResilienceDependency(StrEnum):
    """doc 24 §126 resilience matrix — the 9 dependencies this platform integrates
    with, each getting its own independent circuit breaker so one unstable dependency
    never trips the others."""

    ENTERPRISE_API = "ENTERPRISE_API"
    SLM = "SLM"
    RAG = "RAG"
    VECTOR = "VECTOR"
    MCP = "MCP"
    SERVICE_BUS = "SERVICE_BUS"
    CACHE = "CACHE"
    MEMORY = "MEMORY"
    LANGFUSE = "LANGFUSE"


class ResilienceRegistry:
    """One independent `CircuitBreaker` per dependency (doc 24 §61-62)."""

    def __init__(self, settings: CircuitBreakerSettings) -> None:
        self._settings = settings
        self._breakers: dict[ResilienceDependency, CircuitBreaker] = {
            dependency: CircuitBreaker(settings) for dependency in ResilienceDependency
        }

    def get(self, dependency: ResilienceDependency) -> CircuitBreaker:
        return self._breakers[dependency]
