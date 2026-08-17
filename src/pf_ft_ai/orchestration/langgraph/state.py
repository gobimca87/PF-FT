from __future__ import annotations

from typing import Any, TypedDict


class GraphState(TypedDict):
    """Typed LangGraph execution state (doc 4 §20, doc 7 §26)."""

    request: dict[str, Any]
    conversation: dict[str, Any]
    session: dict[str, Any]
    claims: dict[str, Any]
    workflow: dict[str, Any]
    intent: dict[str, Any]
    entities: dict[str, Any]
    context_requirements: dict[str, Any]
    erc_reference: dict[str, Any]
    knowledge_context: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    pending_action: dict[str, Any] | None
    current_node: str
    execution_status: str
    step_count: int
    error: dict[str, Any] | None
    trace_context: dict[str, Any]
