import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.orchestration.langgraph.nodes import NodeKind, NodeRegistry
from pf_ft_ai.orchestration.langgraph.state import GraphState


async def _handler(state: GraphState) -> GraphState:
    return state


def test_should_resolve_kind_from_standard_node_catalog() -> None:
    registry = NodeRegistry()

    node = registry.register("reason", _handler)

    assert node.kind is NodeKind.AI_ASSISTED


def test_should_classify_deterministic_standard_node() -> None:
    registry = NodeRegistry()

    node = registry.register("authorize_tool", _handler)

    assert node.kind is NodeKind.DETERMINISTIC


def test_should_accept_explicit_kind_for_a_custom_node() -> None:
    registry = NodeRegistry()

    node = registry.register("custom_step", _handler, kind=NodeKind.DETERMINISTIC)

    assert node.kind is NodeKind.DETERMINISTIC


def test_should_reject_unknown_node_without_explicit_kind() -> None:
    registry = NodeRegistry()

    with pytest.raises(ConfigurationError, match="Unknown node_id"):
        registry.register("mystery_step", _handler)


def test_should_list_and_get_registered_nodes() -> None:
    registry = NodeRegistry()
    registry.register("reason", _handler)
    registry.register("authorize_tool", _handler)

    assert {node.node_id for node in registry.list_nodes()} == {"reason", "authorize_tool"}
    assert registry.get("reason") is not None
    assert registry.get("missing") is None
