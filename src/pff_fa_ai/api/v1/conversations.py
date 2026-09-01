from __future__ import annotations

from fastapi import APIRouter, Depends

from pff_fa_ai.api.dependencies import (
    get_claims_context,
    get_conversation_service,
    get_correlation_ids,
    get_session_service,
)
from pff_fa_ai.api.v1.envelope import ResponseEnvelope
from pff_fa_ai.application.conversation.dto import ConversationView, MessageView
from pff_fa_ai.application.conversation.service import ConversationService
from pff_fa_ai.application.session.service import SessionService
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import new_id

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("", response_model=ResponseEnvelope[ConversationView])
async def create_conversation(
    claims: ClaimsContext = Depends(get_claims_context),
    correlation: tuple[str, str] = Depends(get_correlation_ids),
    conversation_service: ConversationService = Depends(get_conversation_service),
    session_service: SessionService = Depends(get_session_service),
) -> ResponseEnvelope[ConversationView]:
    request_id, _correlation_id = correlation
    conversation_id = new_id("conv")
    session_id = new_id("sess")
    await session_service.create_session(
        session_id=session_id, conversation_id=conversation_id, user_reference=claims.subject
    )
    conversation = await conversation_service.start_conversation(
        conversation_id=conversation_id, session_id=session_id, claims=claims
    )
    return ResponseEnvelope[ConversationView](
        request_id=request_id,
        conversation_id=conversation.conversation_id,
        status=conversation.status.value,
        data=ConversationView.from_conversation(conversation),
    )


@router.get("/{conversation_id}", response_model=ResponseEnvelope[ConversationView])
async def get_conversation(
    conversation_id: str,
    claims: ClaimsContext = Depends(get_claims_context),
    correlation: tuple[str, str] = Depends(get_correlation_ids),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ResponseEnvelope[ConversationView]:
    request_id, _correlation_id = correlation
    conversation = await conversation_service.resolve_conversation(conversation_id, claims=claims)
    return ResponseEnvelope[ConversationView](
        request_id=request_id,
        conversation_id=conversation.conversation_id,
        status=conversation.status.value,
        data=ConversationView.from_conversation(conversation),
    )


@router.get("/{conversation_id}/messages", response_model=ResponseEnvelope[list[MessageView]])
async def list_messages(
    conversation_id: str,
    claims: ClaimsContext = Depends(get_claims_context),
    correlation: tuple[str, str] = Depends(get_correlation_ids),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ResponseEnvelope[list[MessageView]]:
    request_id, _correlation_id = correlation
    conversation = await conversation_service.resolve_conversation(conversation_id, claims=claims)
    messages = await conversation_service.list_messages(conversation_id)
    return ResponseEnvelope[list[MessageView]](
        request_id=request_id,
        conversation_id=conversation.conversation_id,
        status=conversation.status.value,
        data=[MessageView.from_message(message) for message in messages],
    )


@router.post("/{conversation_id}/close", response_model=ResponseEnvelope[ConversationView])
async def close_conversation(
    conversation_id: str,
    claims: ClaimsContext = Depends(get_claims_context),
    correlation: tuple[str, str] = Depends(get_correlation_ids),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ResponseEnvelope[ConversationView]:
    request_id, _correlation_id = correlation
    conversation = await conversation_service.resolve_conversation(conversation_id, claims=claims)
    closed = await conversation_service.close_conversation(conversation)
    return ResponseEnvelope[ConversationView](
        request_id=request_id,
        conversation_id=closed.conversation_id,
        status=closed.status.value,
        data=ConversationView.from_conversation(closed),
    )
