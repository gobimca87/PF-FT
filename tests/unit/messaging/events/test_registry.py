import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.messaging.events.registry import EventRoute, EventRouteRegistry


def test_should_register_and_resolve_a_route() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))

    route = registry.resolve("HIL_TASK_COMPLETED")

    assert route is not None
    assert route.handler == "workflow.resume"


def test_should_return_none_for_an_unregistered_event_type() -> None:
    registry = EventRouteRegistry()

    assert registry.resolve("UNKNOWN_EVENT") is None


def test_should_return_none_for_a_disabled_route() -> None:
    registry = EventRouteRegistry()
    registry.register(
        EventRoute(event_type="OFFICIAL_UPDATED", handler="erc.refresh", enabled=False)
    )

    assert registry.resolve("OFFICIAL_UPDATED") is None


def test_should_reject_a_duplicate_route_registration() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="TEAM_UPDATED", handler="erc.refresh"))

    with pytest.raises(ConfigurationError, match="Duplicate route"):
        registry.register(EventRoute(event_type="TEAM_UPDATED", handler="erc.refresh"))


def test_route_should_carry_a_target_section_for_erc_refresh() -> None:
    route = EventRoute(
        event_type="OFFICIAL_UPDATED", handler="erc.refresh", target_section="officials"
    )

    assert route.target_section == "officials"
