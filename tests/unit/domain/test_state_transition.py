from datetime import UTC, datetime

from pf_ft_ai.domain.state_transition import StateActor, StateTransition


def test_should_capture_a_full_state_transition_record() -> None:
    transition = StateTransition(
        entity_id="wf-123",
        from_state="BUILDING_ERC",
        to_state="REASONING",
        reason="erc_complete",
        actor=StateActor.AGENT,
        version=10,
        occurred_at=datetime.now(UTC),
    )

    assert transition.entity_id == "wf-123"
    assert transition.from_state == "BUILDING_ERC"
    assert transition.to_state == "REASONING"
    assert transition.actor is StateActor.AGENT
