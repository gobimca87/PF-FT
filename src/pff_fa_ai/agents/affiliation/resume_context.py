from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.common.claims import ClaimsContext


class AffiliationResumeContext(BaseModel):
    """Everything `AffiliationAgent._resume()` needs that isn't already on the
    persisted `WorkflowInstance` (which only carries `current_state`/`waiting`, not
    arbitrary agent state — doc 5's `WorkflowInstance` schema is deliberately generic
    across every future agent, not affiliation-specific)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claims: ClaimsContext
    conversation_id: str


class AffiliationResumeContextStore:
    """In-memory, keyed by `workflow_instance_id` — matches the same "interface now,
    concrete adapter later" posture as `InMemoryWorkflowRepository`; a durable store is
    an infrastructure decision for whenever this agent is actually deployed, not a
    concern this reference implementation needs to resolve."""

    def __init__(self) -> None:
        self._contexts: dict[str, AffiliationResumeContext] = {}

    def save(self, workflow_instance_id: str, context: AffiliationResumeContext) -> None:
        self._contexts[workflow_instance_id] = context

    def get(self, workflow_instance_id: str) -> AffiliationResumeContext | None:
        return self._contexts.get(workflow_instance_id)
