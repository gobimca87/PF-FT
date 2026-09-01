from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from pff_fa_ai.agents.affiliation.dependencies import AffiliationDependencies
from pff_fa_ai.agents.affiliation.graph import build_affiliation_graph
from pff_fa_ai.agents.affiliation.resume_context import AffiliationResumeContext
from pff_fa_ai.agents.affiliation.steps import (
    FAILED_STATUS,
    RESUME_ENTRY_STEP,
    STEP_ORDER,
    WAITING_FOR_EVENT_STATUS,
)
from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.agents.result import AgentError, AgentExecutionResult
from pff_fa_ai.agents.states import AgentRunStatus
from pff_fa_ai.common.error_category import ErrorCategory
from pff_fa_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pff_fa_ai.domain.workflow.states import WaitingType, WorkflowStatus
from pff_fa_ai.orchestration.langgraph.graph_builder import COMPLETED_STATUS
from pff_fa_ai.orchestration.langgraph.state import GraphState

WORKFLOW_TYPE = "affiliation"
WORKFLOW_VERSION = "1.0.0"
EXPECTED_EVENT_TYPE = "affiliation.application.status_changed"


def _initial_state(context: AgentExecutionContext) -> GraphState:
    return {
        "request": {"user_message": context.user_message},
        "conversation": {"conversation_id": context.conversation_id},
        "session": {"session_id": context.session_id},
        "claims": context.claims.model_dump(),
        "workflow": {"workflow_instance_id": context.workflow_instance_id},
        "intent": {},
        "entities": {},
        "context_requirements": {},
        "erc_reference": {},
        "knowledge_context": [],
        "tool_results": [],
        "pending_action": None,
        "current_node": STEP_ORDER[0],
        "execution_status": "RUNNING",
        "step_count": 0,
        "error": None,
        "trace_context": {},
    }


def _error_result(*, code: str, message: str) -> AgentExecutionResult:
    return AgentExecutionResult(
        status=AgentRunStatus.FAILED,
        errors=[
            AgentError(
                category=ErrorCategory.DEPENDENCY, code=code, message_safe=message, retryable=False
            )
        ],
    )


def _result_from_failed_state(state: GraphState) -> AgentExecutionResult:
    error = state.get("error") or {"code": "UNKNOWN", "message": "Affiliation agent failed"}
    return _error_result(code=error["code"], message=error["message"])


def _result_from_completed_state(state: GraphState) -> AgentExecutionResult:
    erc_reference = state["erc_reference"]
    return AgentExecutionResult(
        status=AgentRunStatus.COMPLETED,
        response=state["entities"].get("response_text"),
        erc_reference=erc_reference.get("erc_id") if erc_reference else None,
    )


def _build_waiting_info(application_status: str) -> WaitingInfo:
    return WaitingInfo(
        type=WaitingType.WAITING_FOR_EXTERNAL_EVENT,
        reason=f"Affiliation application status is {application_status}",
        created_at=datetime.now(UTC),
        resume_node=RESUME_ENTRY_STEP,
        expected_event_type=EXPECTED_EVENT_TYPE,
    )


class AffiliationAgent:
    """doc 4 §72 / doc 7 §133-135 — DEVELOPMENT-GUIDE Phase 23's reference business
    agent, implementing the `Agent` protocol. Runs the full step sequence
    (`steps.STEP_ORDER`) on a fresh conversation; a workflow already
    `WAITING_FOR_EXTERNAL_EVENT` gets an honest "still waiting" answer without
    re-running the pipeline; a workflow an event handler has moved to `RESUMING`
    re-enters at `steps.RESUME_ENTRY_STEP` (doc 7 §134's async path)."""

    def __init__(self, deps: AffiliationDependencies) -> None:
        self._deps = deps
        self._graph = build_affiliation_graph(deps)

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        existing = await self._deps.workflow_repository.get(context.workflow_instance_id)

        if existing is not None and existing.status is WorkflowStatus.RESUMING:
            return await self._resume(context, existing)

        if existing is not None and existing.status is WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT:
            return self._still_waiting_result(existing)

        return await self._run_fresh(context)

    async def _run_fresh(self, context: AgentExecutionContext) -> AgentExecutionResult:
        final_state = cast(GraphState, await self._graph.ainvoke(_initial_state(context)))

        if final_state["execution_status"] == FAILED_STATUS:
            return _result_from_failed_state(final_state)

        if final_state["execution_status"] == WAITING_FOR_EVENT_STATUS:
            return await self._persist_waiting(context, final_state)

        now = datetime.now(UTC)
        await self._deps.workflow_repository.create(
            WorkflowInstance(
                workflow_instance_id=context.workflow_instance_id,
                workflow_type=WORKFLOW_TYPE,
                workflow_version=WORKFLOW_VERSION,
                status=WorkflowStatus.COMPLETED,
                current_state="finalize_response",
                organization_id=context.claims.organization,
                started_at=now,
                updated_at=now,
            )
        )
        return _result_from_completed_state(final_state)

    async def _persist_waiting(
        self, context: AgentExecutionContext, final_state: GraphState
    ) -> AgentExecutionResult:
        now = datetime.now(UTC)
        waiting = _build_waiting_info(final_state["entities"]["application"]["status"])
        await self._deps.workflow_repository.create(
            WorkflowInstance(
                workflow_instance_id=context.workflow_instance_id,
                workflow_type=WORKFLOW_TYPE,
                workflow_version=WORKFLOW_VERSION,
                status=WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
                current_state=RESUME_ENTRY_STEP,
                organization_id=context.claims.organization,
                started_at=now,
                updated_at=now,
                waiting=waiting,
            )
        )
        self._deps.resume_context_store.save(
            context.workflow_instance_id,
            AffiliationResumeContext(
                claims=context.claims, conversation_id=context.conversation_id
            ),
        )
        return AgentExecutionResult(
            status=AgentRunStatus.WAITING_FOR_EVENT,
            response=final_state["entities"].get("response_text"),
            waiting=waiting,
        )

    def _still_waiting_result(self, existing: WorkflowInstance) -> AgentExecutionResult:
        reason = (
            existing.waiting.reason if existing.waiting else "Still waiting on an enterprise event."
        )
        return AgentExecutionResult(
            status=AgentRunStatus.WAITING_FOR_EVENT, response=reason, waiting=existing.waiting
        )

    async def _resume(
        self, context: AgentExecutionContext, existing: WorkflowInstance
    ) -> AgentExecutionResult:
        resume_context = self._deps.resume_context_store.get(context.workflow_instance_id)
        if resume_context is None:
            return _error_result(
                code="RESUME_CONTEXT_MISSING", message="No saved context to resume from"
            )

        state = _initial_state(context)
        state["claims"] = resume_context.claims.model_dump()
        state["conversation"] = {"conversation_id": resume_context.conversation_id}
        state["current_node"] = RESUME_ENTRY_STEP
        state["entities"] = {"club_id": existing.organization_id}

        final_state = cast(GraphState, await self._graph.ainvoke(state))

        if final_state["execution_status"] == FAILED_STATUS:
            return _result_from_failed_state(final_state)

        if final_state["execution_status"] == WAITING_FOR_EVENT_STATUS:
            # doc 7 §134 / flow doc Scenario 6: CFA approves with a fee — the
            # workflow resumes only to discover it must now wait again, for payment
            # this time. `transition()` re-persists a *new* `WaitingInfo` rather than
            # calling `_persist_waiting()`'s `create()`, since the workflow record
            # already exists.
            waiting = _build_waiting_info(final_state["entities"]["application"]["status"])
            await self._deps.workflow_repository.transition(
                context.workflow_instance_id,
                status=WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
                current_state=RESUME_ENTRY_STEP,
                expected_version=existing.version,
                waiting=waiting,
            )
            return AgentExecutionResult(
                status=AgentRunStatus.WAITING_FOR_EVENT,
                response=final_state["entities"].get("response_text"),
                waiting=waiting,
            )

        if final_state["execution_status"] != COMPLETED_STATUS:
            # doc 7 §134's resume path ends at RESPONSE/COMPLETE or another wait for
            # the scenarios this reference implementation covers (6-9) — anything
            # else is treated as a failure rather than left in an inconsistent state.
            return _error_result(
                code="RESUME_DID_NOT_COMPLETE",
                message=f"Resume ended in status {final_state['execution_status']}",
            )

        await self._deps.workflow_repository.transition(
            context.workflow_instance_id,
            status=WorkflowStatus.COMPLETED,
            current_state="finalize_response",
            expected_version=existing.version,
        )
        return _result_from_completed_state(final_state)
