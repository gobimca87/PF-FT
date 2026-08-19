from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from pf_ft_ai.agents.affiliation.dependencies import AffiliationDependencies
from pf_ft_ai.agents.affiliation.erc import build_affiliation_erc, build_erc_section
from pf_ft_ai.agents.affiliation.models import (
    ApplicationSummary,
    ClubSummary,
    InsuranceSummary,
    OfficialSummary,
    PaymentStatusSummary,
    ProductSummary,
    TeamSummary,
)
from pf_ft_ai.agents.affiliation.persona import build_response_text
from pf_ft_ai.agents.affiliation.portal import resolve_affiliation_portal_links
from pf_ft_ai.agents.affiliation.states import WAITING_STATUSES, AffiliationApplicationStatus
from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.context.collection.aggregator import aggregate_records
from pf_ft_ai.context.collection.batching import split_into_batches
from pf_ft_ai.context.erc.models import ErcSection
from pf_ft_ai.guardrails.models import GuardrailContext
from pf_ft_ai.guardrails.states import GuardrailBoundary, GuardrailDecision
from pf_ft_ai.integration.tools.models import ToolExecutionRequest
from pf_ft_ai.integration.tools.states import ToolCallStatus
from pf_ft_ai.orchestration.langgraph.graph_builder import COMPLETED_STATUS
from pf_ft_ai.orchestration.langgraph.state import GraphState

AGENT_ID = "affiliation_agent"
WAITING_FOR_EVENT_STATUS = "WAITING_FOR_EVENT"
FAILED_STATUS = "FAILED"

STEP_ORDER: tuple[str, ...] = (
    "understand_request",
    "identify_club",
    "collect_application_context",
    "collect_entity_context",
    "build_and_validate_erc",
    "maybe_retrieve_rag",
    "reason_about_status",
    "finalize_response",
)

# doc 7 §134 "Affiliation Agent — Async Path": resume skips straight to a refresh +
# REASON + RESPONSE, not the full pipeline — club/teams/officials/insurance rarely
# change while an application sits in PENDING_CFA/INVOICED, only the application
# (and, if invoiced, payment) status does.
RESUME_ENTRY_STEP = "refresh_application"

_NEXT_STEP: dict[str, str] = {
    STEP_ORDER[index]: STEP_ORDER[index + 1] for index in range(len(STEP_ORDER) - 1)
} | {
    STEP_ORDER[-1]: STEP_ORDER[-1],  # terminal — the graph stops via `execution_status`
    RESUME_ENTRY_STEP: "reason_about_status",
}


def _advance(state: GraphState, step: str, **entity_updates: Any) -> GraphState:
    entities = {**state["entities"], **entity_updates} if entity_updates else state["entities"]
    return {**state, "current_node": _NEXT_STEP[step], "entities": entities}


def _fail(state: GraphState, *, code: str, message: str) -> GraphState:
    return {**state, "execution_status": FAILED_STATUS, "error": {"code": code, "message": message}}


async def _call_tool(
    deps: AffiliationDependencies,
    *,
    tool_id: str,
    claims: ClaimsContext,
    arguments: dict[str, str],
    workflow_instance_id: str,
) -> tuple[bool, Any, str | None]:
    """Returns `(succeeded, data, error_message)`."""
    result = await deps.tool_executor.execute(
        ToolExecutionRequest(
            tool_id=tool_id,
            agent_id=AGENT_ID,
            claims=claims,
            arguments=arguments,
            workflow_instance_id=workflow_instance_id,
            operation_id=f"{workflow_instance_id}-{tool_id}",
        )
    )
    if result.status is not ToolCallStatus.TOOL_COMPLETED:
        message = result.error.message if result.error else f"{tool_id} did not complete"
        return False, None, message
    return True, result.data, None


async def understand_request(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    message = state["request"].get("user_message", "").lower()
    intent = "affiliation_payment" if "pay" in message else "affiliation_status"
    return {
        **_advance(state, "understand_request"),
        "intent": {"intent": intent, "confidence": 1.0},
    }


async def identify_club(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    club_id = state["claims"].get("organization")
    if not club_id:
        return _fail(state, code="MISSING_CLUB", message="No organization claim to identify a club")
    return _advance(state, "identify_club", club_id=club_id)


async def collect_application_context(
    state: GraphState, deps: AffiliationDependencies
) -> GraphState:
    claims = ClaimsContext.model_validate(state["claims"])
    club_id = state["entities"]["club_id"]
    workflow_instance_id = state["workflow"]["workflow_instance_id"]

    (club_ok, club_data, club_err), (app_ok, app_data, app_err) = await asyncio.gather(
        _call_tool(
            deps,
            tool_id="affiliation.get_club",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
        _call_tool(
            deps,
            tool_id="affiliation.get_application",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
    )
    if not club_ok:
        return _fail(state, code="GET_CLUB_FAILED", message=club_err or "get_club failed")
    if not app_ok:
        return _fail(
            state, code="GET_APPLICATION_FAILED", message=app_err or "get_application failed"
        )

    return _advance(
        state,
        "collect_application_context",
        club=ClubSummary.model_validate(club_data).model_dump(mode="json"),
        application=ApplicationSummary.model_validate(app_data).model_dump(mode="json"),
    )


def _batch_process_records(
    records: list[dict[str, Any]], *, batch_size: int, expected_count: int, key_field: str
) -> list[dict[str, Any]]:
    """doc 4 §72 point 8 / doc 5 §93: large collections are processed in
    `batch_size`-record batches and then deduplicated/verified for completeness — the
    same pipeline `tests/component/test_erc_context_component.py` already proves for
    100+ synthetic entities, applied here to whatever `records` actually came back."""
    batches = split_into_batches(len(records), batch_size=batch_size)
    collected: list[dict[str, Any]] = []
    for batch in batches:
        collected.extend(records[batch.start - 1 : batch.end])
    result = aggregate_records(
        collected, key=lambda record: record[key_field], expected_count=expected_count
    )
    return list(result.records)


async def collect_entity_context(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    claims = ClaimsContext.model_validate(state["claims"])
    club_id = state["entities"]["club_id"]
    workflow_instance_id = state["workflow"]["workflow_instance_id"]
    batch_size = deps.settings.team_official_batch_size

    results = await asyncio.gather(
        _call_tool(
            deps,
            tool_id="affiliation.get_teams",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
        _call_tool(
            deps,
            tool_id="affiliation.get_officials",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
        _call_tool(
            deps,
            tool_id="affiliation.get_insurance",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
    )
    (
        (teams_ok, teams_data, teams_err),
        (officials_ok, officials_data, officials_err),
        (
            insurance_ok,
            insurance_data,
            insurance_err,
        ),
    ) = results
    if not teams_ok:
        return _fail(state, code="GET_TEAMS_FAILED", message=teams_err or "get_teams failed")
    if not officials_ok:
        return _fail(
            state,
            code="GET_OFFICIALS_FAILED",
            message=officials_err or "get_officials failed",
        )
    if not insurance_ok:
        return _fail(
            state,
            code="GET_INSURANCE_FAILED",
            message=insurance_err or "get_insurance failed",
        )

    team_items = teams_data.get("items", [])
    official_items = officials_data.get("items", [])
    teams = _batch_process_records(
        team_items,
        batch_size=batch_size,
        expected_count=teams_data.get("total", len(team_items)),
        key_field="team_id",
    )
    officials = _batch_process_records(
        official_items,
        batch_size=batch_size,
        expected_count=officials_data.get("total", len(official_items)),
        key_field="official_id",
    )

    application = state["entities"]["application"]
    products: list[dict[str, Any]] = []
    if application.get("application_id"):
        products_ok, products_data, products_err = await _call_tool(
            deps,
            tool_id="affiliation.get_products",
            claims=claims,
            arguments={"applicationId": application["application_id"]},
            workflow_instance_id=workflow_instance_id,
        )
        if not products_ok:
            return _fail(
                state,
                code="GET_PRODUCTS_FAILED",
                message=products_err or "get_products failed",
            )
        products = products_data.get("items", [])

    return _advance(
        state,
        "collect_entity_context",
        teams=[TeamSummary.model_validate(team).model_dump(mode="json") for team in teams],
        officials=[
            OfficialSummary.model_validate(official).model_dump(mode="json")
            for official in officials
        ],
        insurance=InsuranceSummary.model_validate(insurance_data).model_dump(mode="json"),
        products=[
            ProductSummary.model_validate(product).model_dump(mode="json") for product in products
        ],
    )


async def build_and_validate_erc(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    entities = state["entities"]
    workflow_instance_id = state["workflow"]["workflow_instance_id"]
    conversation_id = state["conversation"]["conversation_id"]

    sections: dict[str, ErcSection] = {
        "club": build_erc_section(
            name="club",
            data=entities["club"],
            api_id="enterprise.affiliation.get_club",
            endpoint_ref="/api/v1/clubs/{clubId}",
        ),
        "application": build_erc_section(
            name="application",
            data=entities["application"],
            api_id="enterprise.affiliation.get_application",
            endpoint_ref="/api/v1/clubs/{clubId}/affiliation-application",
        ),
        "teams": build_erc_section(
            name="teams",
            data={"items": entities["teams"]},
            api_id="enterprise.affiliation.get_teams",
            endpoint_ref="/api/v1/clubs/{clubId}/teams",
        ),
        "officials": build_erc_section(
            name="officials",
            data={"items": entities["officials"]},
            api_id="enterprise.affiliation.get_officials",
            endpoint_ref="/api/v1/clubs/{clubId}/officials",
        ),
        "insurance": build_erc_section(
            name="insurance",
            data=entities["insurance"],
            api_id="enterprise.affiliation.get_insurance",
            endpoint_ref="/api/v1/clubs/{clubId}/insurance",
        ),
        "products": build_erc_section(
            name="products",
            data={"items": entities["products"]},
            api_id="enterprise.affiliation.get_products",
            endpoint_ref="/api/v1/affiliation-applications/{applicationId}/products",
        ),
    }
    # doc 8 §71 completeness/validation: this step always supplies exactly
    # `erc.REQUIRED_SECTIONS` (every entity was already fetched by the two steps
    # before this one, or this step would never have been reached — a partial ERC
    # from a partially-failed collection isn't a state this pipeline produces), so
    # `erc.completeness.missing_sections` is always empty here by construction. The
    # general incompleteness check itself is real and tested directly against
    # `build_affiliation_erc()` (see `test_erc.py`) for whatever future caller
    # assembles a genuinely partial ERC.
    erc = build_affiliation_erc(
        erc_id=f"erc-{workflow_instance_id}",
        workflow_instance_id=workflow_instance_id,
        conversation_id=conversation_id,
        sections=sections,
    )

    return {
        **_advance(state, "build_and_validate_erc"),
        "erc_reference": erc.model_dump(mode="json"),
    }


async def maybe_retrieve_rag(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    """doc 7 §133 "NEED RAG?" branch — always skips today: `config/enterprise` and the
    RAG corpus behind it (Phase 8) ship empty pending real policy content, so there is
    nothing to retrieve. The branch is real and wired, not removed, so it activates the
    moment real content exists without further graph changes."""
    return _advance(state, "maybe_retrieve_rag")


async def refresh_application(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    """doc 7 §134 resume entry point. Re-fetches `get_application` — the authoritative
    enterprise result always wins over whatever was cached in `entities["application"]`
    from the original run (CLAUDE.md Golden Rule: Enterprise API > ERC), never merged
    or reconciled with the stale value. Also re-fetches `get_club`, since a resumed run
    starts with only `club_id` in `entities` (the persisted `WorkflowInstance` doesn't
    carry the full original entity bag — see `resume_context.py`) and
    `finalize_response` needs the club name for the response text."""
    claims = ClaimsContext.model_validate(state["claims"])
    club_id = state["entities"]["club_id"]
    workflow_instance_id = state["workflow"]["workflow_instance_id"]

    (club_ok, club_data, club_err), (app_ok, app_data, app_err) = await asyncio.gather(
        _call_tool(
            deps,
            tool_id="affiliation.get_club",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
        _call_tool(
            deps,
            tool_id="affiliation.get_application",
            claims=claims,
            arguments={"clubId": club_id},
            workflow_instance_id=workflow_instance_id,
        ),
    )
    if not club_ok:
        return _fail(state, code="GET_CLUB_FAILED", message=club_err or "get_club failed")
    if not app_ok:
        return _fail(
            state, code="GET_APPLICATION_FAILED", message=app_err or "get_application failed"
        )

    # doc 7 §134 "ERC INVALIDATION -> ERC REFRESH": conceptually the ERC's application
    # section should be refreshed too. In this reference implementation resume always
    # starts from a fresh `GraphState` (`AffiliationAgent._resume()` — there is no
    # durable ERC store to reload the original snapshot from, doc 7 §54's ADR-pending
    # vector/memory-store decisions apply to ERC persistence too), so `erc_reference`
    # is empty at this point and there is nothing to patch. This still builds the
    # fresh values `finalize_response` needs either way.
    fresh_club = ClubSummary.model_validate(club_data).model_dump(mode="json")
    fresh_application = ApplicationSummary.model_validate(app_data).model_dump(mode="json")

    return _advance(state, RESUME_ENTRY_STEP, club=fresh_club, application=fresh_application)


def _outcome_for_status(status: AffiliationApplicationStatus) -> str:
    if status is AffiliationApplicationStatus.COMPLETE:
        return "complete"
    if status is AffiliationApplicationStatus.PENDING_CFA:
        return "waiting_cfa"
    if status is AffiliationApplicationStatus.INVOICED:
        return "waiting_payment"
    if status is AffiliationApplicationStatus.REJECTED:
        return "rejected"
    if status is AffiliationApplicationStatus.CANCELLED:
        return "cancelled"
    return "in_progress"


async def reason_about_status(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    """Deterministic — the enterprise `get_application` result (already in
    `entities["application"]`) is the sole source of truth for the status (CLAUDE.md
    Golden Rule); this step only decides which kind of response to build."""
    application = state["entities"]["application"]
    status = AffiliationApplicationStatus(application["status"])
    return _advance(state, "reason_about_status", outcome_category=_outcome_for_status(status))


async def _maybe_fetch_payment_status(
    state: GraphState, deps: AffiliationDependencies
) -> dict[str, Any] | None:
    application = state["entities"]["application"]
    if application["status"] != AffiliationApplicationStatus.INVOICED.value:
        return None
    claims = ClaimsContext.model_validate(state["claims"])
    ok, data, _err = await _call_tool(
        deps,
        tool_id="affiliation.get_payment_status",
        claims=claims,
        arguments={"applicationId": application["application_id"]},
        workflow_instance_id=state["workflow"]["workflow_instance_id"],
    )
    return PaymentStatusSummary.model_validate(data).model_dump(mode="json") if ok else None


async def finalize_response(state: GraphState, deps: AffiliationDependencies) -> GraphState:
    application = state["entities"]["application"]
    status = AffiliationApplicationStatus(application["status"])
    payment_status = await _maybe_fetch_payment_status(state, deps)

    response_text = build_response_text(
        club=state["entities"]["club"],
        application=application,
        outcome_category=state["entities"]["outcome_category"],
        payment_status=payment_status,
    )

    guardrail_result = await deps.guardrails.evaluate(
        GuardrailBoundary.OUTPUT,
        GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content=response_text),
    )
    if guardrail_result.decision is GuardrailDecision.BLOCK:
        return _fail(state, code="OUTPUT_BLOCKED", message="Response blocked by output guardrail")

    links = resolve_affiliation_portal_links(
        deps,
        claims=ClaimsContext.model_validate(state["claims"]),
        club_id=state["entities"]["club_id"],
        application_id=application["application_id"],
    )

    entity_updates = {
        "response_text": response_text,
        "portal_links": [link.model_dump(mode="json") for link in links],
        "payment_status": payment_status,
    }
    execution_status = WAITING_FOR_EVENT_STATUS if status in WAITING_STATUSES else COMPLETED_STATUS
    return {
        **_advance(state, "finalize_response", **entity_updates),
        "execution_status": execution_status,
    }


StepHandler = Callable[[GraphState, AffiliationDependencies], Awaitable[GraphState]]

STEP_HANDLERS: dict[str, StepHandler] = {
    "understand_request": understand_request,
    "identify_club": identify_club,
    "collect_application_context": collect_application_context,
    "collect_entity_context": collect_entity_context,
    "build_and_validate_erc": build_and_validate_erc,
    "maybe_retrieve_rag": maybe_retrieve_rag,
    "reason_about_status": reason_about_status,
    "finalize_response": finalize_response,
    RESUME_ENTRY_STEP: refresh_application,
}
