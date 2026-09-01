from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

import structlog
from langfuse import Langfuse

from pff_fa_ai.common.correlation import CorrelationContext
from pff_fa_ai.configuration.models import LangfuseSettings

_logger = structlog.get_logger(__name__)


class ObservabilityClient(Protocol):
    """doc 24 §42-43 — Langfuse-shaped tracing, behind a provider-independent port."""

    def record_event(
        self,
        *,
        name: str,
        correlation: CorrelationContext,
        metadata: Mapping[str, Any] | None = None,
    ) -> None: ...

    def flush(self) -> None: ...


class NullObservabilityClient:
    """Used whenever Langfuse is disabled/unconfigured (doc 24 §48) — every call is a
    genuine no-op, not a stub that happens to do nothing today."""

    def record_event(
        self,
        *,
        name: str,
        correlation: CorrelationContext,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        return None

    def flush(self) -> None:
        return None


class LangfuseObservabilityClient:
    """doc 24 §48: Langfuse must never break core execution — every SDK call is caught
    and logged, never propagated, regardless of what fails inside the SDK."""

    def __init__(self, client: Langfuse) -> None:
        self._client = client

    def record_event(
        self,
        *,
        name: str,
        correlation: CorrelationContext,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        try:
            self._client.trace(
                name=name,
                id=correlation.correlation_id,
                session_id=correlation.session_id,
                metadata={
                    **(metadata or {}),
                    "request_id": correlation.request_id,
                    "conversation_id": correlation.conversation_id,
                    "workflow_instance_id": correlation.workflow_instance_id,
                },
            )
        except Exception:  # observability must degrade, never propagate (doc 24 §48)
            _logger.warning(
                "langfuse_trace_failed", name=name, correlation_id=correlation.correlation_id
            )

    def flush(self) -> None:
        try:
            self._client.flush()
        except Exception:  # same rationale as record_event
            _logger.warning("langfuse_flush_failed")


def build_observability_client(settings: LangfuseSettings) -> ObservabilityClient:
    if (
        not settings.enabled
        or not settings.host
        or not settings.public_key
        or not settings.secret_key
    ):
        return NullObservabilityClient()
    langfuse_client = Langfuse(
        host=settings.host, public_key=settings.public_key, secret_key=settings.secret_key
    )
    return LangfuseObservabilityClient(langfuse_client)
