from __future__ import annotations

from fastapi import APIRouter, Depends

from pff_fa_ai.api.dependencies import get_correlation_ids, get_session_service
from pff_fa_ai.api.v1.envelope import ResponseEnvelope
from pff_fa_ai.application.session.dto import SessionView
from pff_fa_ai.application.session.service import SessionService

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=ResponseEnvelope[SessionView])
async def get_session(
    session_id: str,
    correlation: tuple[str, str] = Depends(get_correlation_ids),
    session_service: SessionService = Depends(get_session_service),
) -> ResponseEnvelope[SessionView]:
    request_id, _correlation_id = correlation
    session = await session_service.resolve_session(session_id)
    return ResponseEnvelope[SessionView](
        request_id=request_id, status=session.status.value, data=SessionView.from_session(session)
    )
