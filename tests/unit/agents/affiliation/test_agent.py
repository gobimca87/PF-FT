from datetime import UTC, datetime

import httpx

from pf_ft_ai.agents.affiliation.agent import AffiliationAgent
from pf_ft_ai.agents.affiliation.resume_handler import AffiliationWorkflowResumeHandler
from pf_ft_ai.agents.states import AgentRunStatus
from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.domain.workflow.entities import WorkflowInstance
from pf_ft_ai.domain.workflow.states import WorkflowStatus
from pf_ft_ai.infrastructure.persistence import InMemoryWorkflowRepository
from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute
from pf_ft_ai.messaging.handlers.workflow_resume import WorkflowResumeService
from tests.unit.agents.affiliation.support import (
    APPLICATION_ID,
    build_test_dependencies,
    enterprise_response_handler,
    make_context,
)


def _event(workflow_instance_id: str) -> EventEnvelope:
    return EventEnvelope(
        event_id=new_id("evt"),
        event_type="affiliation.application.status_changed",
        event_version="1.0",
        source="enterprise",
        subject=APPLICATION_ID,
        occurred_at=datetime.now(UTC),
        published_at=datetime.now(UTC),
        correlation_id=new_id("corr"),
        tenant_id="pff",
        organization_id="club-1",
        workflow_instance_id=workflow_instance_id,
    )


_ROUTE = EventRoute(event_type="affiliation.application.status_changed", handler="workflow.resume")


# --- Scenario 5: Auto-Approve --------------------------------------------------------


async def test_scenario_5_auto_approve_should_complete_immediately() -> None:
    deps = build_test_dependencies(enterprise_response_handler(application_status="COMPLETE"))
    agent = AffiliationAgent(deps)

    result = await agent.execute(make_context())

    assert result.status is AgentRunStatus.COMPLETED
    assert result.response is not None
    assert "GOAL" in result.response
    assert "Testville FC" in result.response
    assert result.erc_reference is not None


async def test_scenario_5_should_persist_a_completed_workflow_instance() -> None:
    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(
        enterprise_response_handler(application_status="COMPLETE"),
        workflow_repository=workflow_repository,
    )
    agent = AffiliationAgent(deps)
    context = make_context()

    await agent.execute(context)

    workflow = await workflow_repository.get(context.workflow_instance_id)
    assert workflow is not None
    assert workflow.status is WorkflowStatus.COMPLETED


async def test_scenario_9_zero_fee_approval_should_also_complete_immediately() -> None:
    deps = build_test_dependencies(
        enterprise_response_handler(application_status="COMPLETE", total_fee=0.0)
    )
    agent = AffiliationAgent(deps)

    result = await agent.execute(make_context())

    assert result.status is AgentRunStatus.COMPLETED


async def test_rejected_application_should_produce_a_factual_non_celebratory_response() -> None:
    deps = build_test_dependencies(
        enterprise_response_handler(
            application_status="REJECTED", rejection_reason="Missing safeguarding checks"
        )
    )
    agent = AffiliationAgent(deps)

    result = await agent.execute(make_context())

    assert result.status is AgentRunStatus.COMPLETED
    assert result.response is not None
    assert "GOAL" not in result.response
    assert "Missing safeguarding checks" in result.response


async def test_cancelled_application_should_be_reported_factually() -> None:
    deps = build_test_dependencies(
        enterprise_response_handler(
            application_status="CANCELLED", cancellation_reason="Club withdrew"
        )
    )
    agent = AffiliationAgent(deps)

    result = await agent.execute(make_context())

    assert result.status is AgentRunStatus.COMPLETED
    assert result.response is not None
    assert "Club withdrew" in result.response


# --- Large collections (doc 4 §72 point 8 / DEVELOPMENT-GUIDE Phase 23) -------------


async def test_should_process_100_plus_teams_and_officials_without_data_loss() -> None:
    deps = build_test_dependencies(
        enterprise_response_handler(
            application_status="COMPLETE", team_count=137, official_count=103
        )
    )
    agent = AffiliationAgent(deps)

    result = await agent.execute(make_context())

    assert result.status is AgentRunStatus.COMPLETED


# --- Scenarios 6-9: CFA review -> invoice -> payment -> complete ---------------------


async def test_pending_cfa_should_return_waiting_for_event_and_persist_the_workflow() -> None:
    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(
        enterprise_response_handler(application_status="PENDING_CFA"),
        workflow_repository=workflow_repository,
    )
    agent = AffiliationAgent(deps)
    context = make_context()

    result = await agent.execute(context)

    assert result.status is AgentRunStatus.WAITING_FOR_EVENT
    assert result.waiting is not None
    assert result.waiting.expected_event_type == "affiliation.application.status_changed"

    workflow = await workflow_repository.get(context.workflow_instance_id)
    assert workflow is not None
    assert workflow.status is WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT


async def test_asking_again_while_still_waiting_should_not_rerun_the_pipeline() -> None:
    calls = {"count": 0}
    base_handler = enterprise_response_handler(application_status="PENDING_CFA")

    def counting_handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return base_handler(request)

    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(counting_handler, workflow_repository=workflow_repository)
    agent = AffiliationAgent(deps)
    context = make_context()

    await agent.execute(context)
    calls_after_first = calls["count"]
    result = await agent.execute(context)

    assert result.status is AgentRunStatus.WAITING_FOR_EVENT
    assert calls["count"] == calls_after_first  # no additional enterprise calls made


async def test_full_scenario_6_to_9_chain_via_real_event_driven_resume() -> None:
    """PENDING_CFA -> (CFA approves) -> INVOICED -> (payment confirmed) -> COMPLETE,
    driven entirely by `AffiliationWorkflowResumeHandler` + real Service Bus-shaped
    events, matching doc 7 §134's two-stage async path."""
    status_holder = {"value": "PENDING_CFA"}

    def handler(request: httpx.Request) -> httpx.Response:
        return enterprise_response_handler(
            application_status=status_holder["value"],
            invoice_number="INV-1" if status_holder["value"] != "PENDING_CFA" else None,
            payment_status="PAID" if status_holder["value"] == "COMPLETE" else "AWAITING_PAYMENT",
        )(request)

    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(handler, workflow_repository=workflow_repository)
    agent = AffiliationAgent(deps)
    resume_handler = AffiliationWorkflowResumeHandler(
        WorkflowResumeService(workflow_repository), agent
    )
    context = make_context()

    first = await agent.execute(context)
    assert first.status is AgentRunStatus.WAITING_FOR_EVENT

    status_holder["value"] = "INVOICED"
    approve_outcome = await resume_handler.handle(
        _event(context.workflow_instance_id), route=_ROUTE
    )
    assert approve_outcome.succeeded is True
    after_approval = await workflow_repository.get(context.workflow_instance_id)
    assert after_approval is not None
    assert after_approval.status is WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT
    assert after_approval.waiting is not None
    assert "INVOICED" in after_approval.waiting.reason

    status_holder["value"] = "COMPLETE"
    payment_outcome = await resume_handler.handle(
        _event(context.workflow_instance_id), route=_ROUTE
    )
    assert payment_outcome.succeeded is True
    final_workflow = await workflow_repository.get(context.workflow_instance_id)
    assert final_workflow is not None
    assert final_workflow.status is WorkflowStatus.COMPLETED


# --- Golden authority rule: fresh enterprise API beats stale ERC --------------------


async def test_resume_should_use_the_fresh_status_never_the_stale_cached_one() -> None:
    """CLAUDE.md Golden Rule: Enterprise API > ERC. The original run's ERC/entities
    cache the application as PENDING_CFA; resume must reflect the *fresh*
    `get_application` result (COMPLETE), never fall back to the stale cached value."""
    status_holder = {"value": "PENDING_CFA"}

    def handler(request: httpx.Request) -> httpx.Response:
        return enterprise_response_handler(
            application_status=status_holder["value"],
            invoice_number="INV-1" if status_holder["value"] != "PENDING_CFA" else None,
        )(request)

    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(handler, workflow_repository=workflow_repository)
    agent = AffiliationAgent(deps)
    resume_handler = AffiliationWorkflowResumeHandler(
        WorkflowResumeService(workflow_repository), agent
    )
    context = make_context()

    stale_result = await agent.execute(context)
    assert stale_result.response is not None
    assert "review" in stale_result.response.lower()  # the stale PENDING_CFA framing

    # The enterprise system now reports COMPLETE — a status the *original* run never
    # saw. Nothing in the resume path may prefer the old cached PENDING_CFA value.
    status_holder["value"] = "COMPLETE"
    outcome = await resume_handler.handle(_event(context.workflow_instance_id), route=_ROUTE)

    assert outcome.succeeded is True
    final_workflow = await workflow_repository.get(context.workflow_instance_id)
    assert final_workflow is not None
    assert final_workflow.status is WorkflowStatus.COMPLETED  # fresh status won, not PENDING_CFA


# --- Failure paths ---------------------------------------------------------------------


async def test_should_fail_when_get_club_returns_an_error() -> None:
    deps = build_test_dependencies(
        enterprise_response_handler(not_found_paths=frozenset({"/api/v1/clubs/club-1"}))
    )
    agent = AffiliationAgent(deps)

    result = await agent.execute(make_context())

    assert result.status is AgentRunStatus.FAILED
    assert result.errors
    assert result.errors[0].code == "GET_CLUB_FAILED"


async def test_should_fail_when_no_organization_claim_is_present() -> None:
    deps = build_test_dependencies(enterprise_response_handler())
    agent = AffiliationAgent(deps)
    context = make_context(club_id="")

    result = await agent.execute(context)

    assert result.status is AgentRunStatus.FAILED
    assert result.errors[0].code == "MISSING_CLUB"


async def test_resume_should_fail_when_the_refreshed_tool_call_fails() -> None:
    """Covers `AffiliationAgent._resume()`'s FAILED branch: the original run succeeds
    through to WAITING_FOR_EVENT, but the *resumed* run's `get_club` call fails."""
    club_calls = {"count": 0}
    base_handler = enterprise_response_handler(application_status="PENDING_CFA")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/clubs/club-1"):
            club_calls["count"] += 1
            if club_calls["count"] > 1:  # succeeds on the original run, fails on resume
                return httpx.Response(500, json={"error": "boom"})
        return base_handler(request)

    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(handler, workflow_repository=workflow_repository)
    agent = AffiliationAgent(deps)
    resume_handler = AffiliationWorkflowResumeHandler(
        WorkflowResumeService(workflow_repository), agent
    )
    context = make_context()

    first = await agent.execute(context)
    assert first.status is AgentRunStatus.WAITING_FOR_EVENT

    outcome = await resume_handler.handle(_event(context.workflow_instance_id), route=_ROUTE)

    assert outcome.succeeded is False
    assert outcome.reason_code == "GET_CLUB_FAILED"


async def test_resume_should_fail_cleanly_when_the_graph_lands_in_an_unexpected_status() -> None:
    """Covers `_resume()`'s final "anything else is a failure" branch — exercised by
    substituting a fake compiled graph rather than trying to coax the real one into a
    status it structurally never returns."""

    class _FakeGraph:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            return {**state, "execution_status": "SOMETHING_UNEXPECTED", "error": None}

    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(
        enterprise_response_handler(application_status="PENDING_CFA"),
        workflow_repository=workflow_repository,
    )
    agent = AffiliationAgent(deps)
    resume_handler = AffiliationWorkflowResumeHandler(
        WorkflowResumeService(workflow_repository), agent
    )
    context = make_context()

    first = await agent.execute(context)
    assert first.status is AgentRunStatus.WAITING_FOR_EVENT

    agent._graph = _FakeGraph()  # type: ignore[assignment]
    outcome = await resume_handler.handle(_event(context.workflow_instance_id), route=_ROUTE)

    assert outcome.succeeded is False
    assert outcome.reason_code == "RESUME_DID_NOT_COMPLETE"


async def test_resume_without_a_saved_context_should_fail_cleanly() -> None:
    """A `RESUMING` workflow with no matching `resume_context_store` entry (e.g. the
    agent process restarted and lost its in-memory store) must fail explicitly rather
    than crash or silently invent claims."""
    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(
        enterprise_response_handler(), workflow_repository=workflow_repository
    )
    agent = AffiliationAgent(deps)
    context = make_context()

    await workflow_repository.create(
        WorkflowInstance(
            workflow_instance_id=context.workflow_instance_id,
            workflow_type="affiliation",
            workflow_version="1.0.0",
            status=WorkflowStatus.RESUMING,
            current_state="refresh_application",
            organization_id="club-1",
            started_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    result = await agent.execute(context)

    assert result.status is AgentRunStatus.FAILED
    assert result.errors[0].code == "RESUME_CONTEXT_MISSING"


async def test_payment_status_should_be_fetched_only_when_invoiced() -> None:
    calls = {"payment": 0}
    base_handler = enterprise_response_handler(application_status="COMPLETE")

    def handler(request: httpx.Request) -> httpx.Response:
        if "/payment-status" in request.url.path:
            calls["payment"] += 1
        return base_handler(request)

    deps = build_test_dependencies(handler)
    agent = AffiliationAgent(deps)

    await agent.execute(make_context())

    assert calls["payment"] == 0
