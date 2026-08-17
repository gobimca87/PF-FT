from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


class CorrelationContext(BaseModel):
    """doc 24 §7-8 correlation chain: request_id -> correlation_id ->
    conversation_id/session_id/workflow_instance_id -> the per-execution IDs below,
    populated as each stage actually runs (most requests never touch all of them)."""

    model_config = ConfigDict(frozen=True)

    request_id: str
    correlation_id: str
    conversation_id: str | None = None
    session_id: str | None = None
    workflow_instance_id: str | None = None
    langgraph_run_id: str | None = None
    agent_run_id: str | None = None
    tool_call_id: str | None = None
    api_call_id: str | None = None
    service_bus_message_id: str | None = None
    evaluation_id: str | None = None
