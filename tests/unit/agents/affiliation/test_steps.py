import httpx

from pf_ft_ai.agents.affiliation import steps
from pf_ft_ai.agents.affiliation.states import AffiliationApplicationStatus
from pf_ft_ai.guardrails.models import GuardrailContext, GuardrailResult
from pf_ft_ai.guardrails.states import GuardrailBoundary, GuardrailDecision, GuardrailSeverity
from pf_ft_ai.orchestration.langgraph.state import GraphState
from tests.unit.agents.affiliation.support import (
    build_test_dependencies,
    enterprise_response_handler,
    make_context,
)
from tests.unit.agents.affiliation.test_graph import _initial_state


def _error_code(state: GraphState) -> str:
    error = state["error"]
    assert error is not None
    return str(error["code"])


async def test_collect_application_context_should_fail_when_get_application_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/affiliation-application"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = steps._advance(_initial_state(), "understand_request", club_id="club-1")

    result = await steps.collect_application_context(state, deps)

    assert result["execution_status"] == steps.FAILED_STATUS
    assert _error_code(result) == "GET_APPLICATION_FAILED"


async def test_collect_entity_context_should_fail_when_get_teams_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/teams"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = _initial_state()
    state["entities"] = {"club_id": "club-1", "application": {"application_id": "app-1"}}

    result = await steps.collect_entity_context(state, deps)

    assert result["execution_status"] == steps.FAILED_STATUS
    assert _error_code(result) == "GET_TEAMS_FAILED"


async def test_collect_entity_context_should_fail_when_get_officials_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/officials"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = _initial_state()
    state["entities"] = {"club_id": "club-1", "application": {"application_id": "app-1"}}

    result = await steps.collect_entity_context(state, deps)

    assert _error_code(result) == "GET_OFFICIALS_FAILED"


async def test_collect_entity_context_should_fail_when_get_insurance_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/insurance"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = _initial_state()
    state["entities"] = {"club_id": "club-1", "application": {"application_id": "app-1"}}

    result = await steps.collect_entity_context(state, deps)

    assert _error_code(result) == "GET_INSURANCE_FAILED"


async def test_collect_entity_context_should_fail_when_get_products_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/products"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = _initial_state()
    state["entities"] = {"club_id": "club-1", "application": {"application_id": "app-1"}}

    result = await steps.collect_entity_context(state, deps)

    assert _error_code(result) == "GET_PRODUCTS_FAILED"


async def test_collect_entity_context_should_skip_products_when_no_application_id() -> None:
    deps = build_test_dependencies(enterprise_response_handler())
    state = _initial_state()
    state["entities"] = {"club_id": "club-1", "application": {}}

    result = await steps.collect_entity_context(state, deps)

    assert result["execution_status"] == "RUNNING"
    assert result["entities"]["products"] == []


async def test_build_and_validate_erc_should_assume_all_entities_are_already_present() -> None:
    """This step is only ever reached once `collect_application_context`/
    `collect_entity_context` succeeded, so it doesn't defensively re-check for missing
    entities — a caller that violates that precondition gets a loud `KeyError`, not a
    silently wrong ERC."""
    state = _initial_state()
    state["entities"] = {
        "club": {"club_id": "club-1", "name": "x", "county": "y", "status": "ACTIVE"},
        "application": {
            "application_id": "app-1",
            "club_id": "club-1",
            "season": "2026-27",
            "status": "COMPLETE",
            "total_fee": 0.0,
        },
        "teams": [],
        "officials": [],
        "insurance": {},
        # "products" deliberately omitted
    }

    try:
        await steps.build_and_validate_erc(state, deps=None)  # type: ignore[arg-type]
    except KeyError:
        pass
    else:
        raise AssertionError("expected a KeyError for the missing 'products' entity")


async def test_refresh_application_should_fail_when_get_club_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/clubs/club-1"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = _initial_state()
    state["entities"] = {"club_id": "club-1"}

    result = await steps.refresh_application(state, deps)

    assert _error_code(result) == "GET_CLUB_FAILED"


async def test_refresh_application_should_fail_when_get_application_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/affiliation-application"):
            return httpx.Response(500, json={"error": "boom"})
        return enterprise_response_handler()(request)

    deps = build_test_dependencies(handler)
    state = _initial_state()
    state["entities"] = {"club_id": "club-1"}

    result = await steps.refresh_application(state, deps)

    assert _error_code(result) == "GET_APPLICATION_FAILED"


def test_outcome_for_status_should_default_to_in_progress() -> None:
    assert steps._outcome_for_status(AffiliationApplicationStatus.IN_PROGRESS) == "in_progress"


async def test_finalize_response_should_fail_when_output_guardrail_blocks() -> None:
    class _AlwaysBlockPolicy:
        guardrail_id = "always-block"
        guardrail_version = "1.0.0"

        async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                severity=GuardrailSeverity.CRITICAL,
            )

    deps = build_test_dependencies(enterprise_response_handler(application_status="COMPLETE"))
    deps.guardrails.register(GuardrailBoundary.OUTPUT, _AlwaysBlockPolicy())

    state = _initial_state()
    state["entities"] = {
        "club_id": "club-1",
        "club": {"name": "Testville FC"},
        "application": {
            "application_id": "app-1",
            "status": "COMPLETE",
            "season": "2026-27",
            "total_fee": 0.0,
            "currency": "GBP",
        },
        "outcome_category": "complete",
    }

    result = await steps.finalize_response(state, deps)

    assert result["execution_status"] == steps.FAILED_STATUS
    assert _error_code(result) == "OUTPUT_BLOCKED"


async def test_understand_request_should_recognize_a_payment_question() -> None:
    context = make_context(user_message="I want to pay my invoice")
    state = _initial_state()
    state["request"] = {"user_message": context.user_message}

    result = await steps.understand_request(state, deps=None)  # type: ignore[arg-type]

    assert result["intent"]["intent"] == "affiliation_payment"
