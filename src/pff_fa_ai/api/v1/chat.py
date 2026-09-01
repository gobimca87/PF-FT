from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.api.dependencies import (
    get_claims_context,
    get_conversation_service,
    get_correlation_ids,
    get_session_service,
    get_workflow_orchestrator,
)
from pff_fa_ai.api.v1.envelope import ResponseEnvelope
from pff_fa_ai.application.conversation.service import ConversationService
from pff_fa_ai.application.session.service import SessionService
from pff_fa_ai.application.workflows.orchestrator import OrchestrationRequest, WorkflowOrchestrator
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext, new_id

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation_id: str | None = None
    session_id: str | None = None
    message: str = Field(min_length=1)


class ChatData(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation_id: str
    session_id: str
    workflow_status: str
    response: str


@router.post("/chat", response_model=ResponseEnvelope[ChatData])
async def post_chat(
    payload: ChatRequest,
    claims: ClaimsContext = Depends(get_claims_context),
    correlation: tuple[str, str] = Depends(get_correlation_ids),
    conversation_service: ConversationService = Depends(get_conversation_service),
    session_service: SessionService = Depends(get_session_service),
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
) -> ResponseEnvelope[ChatData]:
    request_id, correlation_id = correlation

    if payload.conversation_id is None:
        conversation_id = new_id("conv")
        session_id = payload.session_id or new_id("sess")
        await session_service.create_session(
            session_id=session_id, conversation_id=conversation_id, user_reference=claims.subject
        )
        conversation = await conversation_service.start_conversation(
            conversation_id=conversation_id, session_id=session_id, claims=claims
        )
    else:
        conversation = await conversation_service.resolve_conversation(
            payload.conversation_id, claims=claims
        )
        session_id = payload.session_id or conversation.session_id
        await session_service.resolve_session(session_id)

    conversation, _user_message = await conversation_service.append_user_message(
        conversation, content=payload.message
    )

    orchestration_request = OrchestrationRequest(
        conversation=conversation,
        user_message=payload.message,
        claims=claims,
        correlation=CorrelationContext(
            request_id=request_id,
            correlation_id=correlation_id,
            conversation_id=conversation.conversation_id,
            session_id=session_id,
        ),
    )
    result = await orchestrator.handle_message(orchestration_request)

    conversation, _assistant_message = await conversation_service.append_assistant_message(
        conversation, content=result.response_message
    )

    data = ChatData(
        conversation_id=conversation.conversation_id,
        session_id=session_id,
        workflow_status=result.status.value,
        response=result.response_message,
    )
    return ResponseEnvelope[ChatData](
        request_id=request_id,
        conversation_id=conversation.conversation_id,
        status=result.status.value,
        message=result.response_message,
        data=data,
    )
