from datetime import UTC, datetime

import pytest

from pff_fa_ai.application.workflows.orchestrator import (
    NullWorkflowOrchestrator,
    OrchestrationRequest,
)
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext
from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.domain.conversation.entities import Conversation
from pff_fa_ai.domain.conversation.states import ConversationStatus


async def test_null_orchestrator_should_raise_a_clear_not_yet_available_error() -> None:
    now = datetime.now(UTC)
    request = OrchestrationRequest(
        conversation=Conversation(
            conversation_id="conv-1",
            user_reference="user-1",
            session_id="sess-1",
            status=ConversationStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        ),
        user_message="hello",
        claims=ClaimsContext(subject="user-1", organization="club-1"),
        correlation=CorrelationContext(request_id="req-1", correlation_id="corr-1"),
    )

    with pytest.raises(WorkflowError, match="Phase 4"):
        await NullWorkflowOrchestrator().handle_message(request)
