from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.orchestration.langgraph.state import GraphState

NodeCallable = Callable[[GraphState], Awaitable[GraphState]]


class NodeKind(StrEnum):
    DETERMINISTIC = "DETERMINISTIC"
    AI_ASSISTED = "AI_ASSISTED"


STANDARD_NODES: dict[str, NodeKind] = {
    "validate_request": NodeKind.DETERMINISTIC,
    "identify_intent": NodeKind.AI_ASSISTED,
    "identify_entities": NodeKind.AI_ASSISTED,
    "determine_context": NodeKind.AI_ASSISTED,
    "collect_context": NodeKind.DETERMINISTIC,
    "build_erc": NodeKind.DETERMINISTIC,
    "validate_erc": NodeKind.DETERMINISTIC,
    "retrieve_rag": NodeKind.DETERMINISTIC,
    "prepare_reasoning_context": NodeKind.DETERMINISTIC,
    "reason": NodeKind.AI_ASSISTED,
    "select_tool": NodeKind.AI_ASSISTED,
    "authorize_tool": NodeKind.DETERMINISTIC,
    "execute_tool": NodeKind.DETERMINISTIC,
    "validate_tool_result": NodeKind.DETERMINISTIC,
    "update_erc": NodeKind.DETERMINISTIC,
    "check_completion": NodeKind.DETERMINISTIC,
    "generate_response": NodeKind.AI_ASSISTED,
    "validate_output": NodeKind.DETERMINISTIC,
    "complete": NodeKind.DETERMINISTIC,
}


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    kind: NodeKind
    handler: NodeCallable


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}

    def register(
        self, node_id: str, handler: NodeCallable, *, kind: NodeKind | None = None
    ) -> GraphNode:
        resolved_kind = kind or STANDARD_NODES.get(node_id)
        if resolved_kind is None:
            raise ConfigurationError(
                f"Unknown node_id '{node_id}': not in STANDARD_NODES and no kind provided"
            )
        node = GraphNode(node_id=node_id, kind=resolved_kind, handler=handler)
        self._nodes[node_id] = node
        return node

    def get(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[GraphNode]:
        return list(self._nodes.values())
