from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.common.claims import ClaimsContext


class AffiliationResumeContext(BaseModel):
    """Everything `AffiliationAgent._resume()` needs that isn't already on the
    persisted `WorkflowInstance` (which only carries `current_state`/`waiting`, not
    arbitrary agent state — doc 5's `WorkflowInstance` schema is deliberately generic
    across every future agent, not affiliation-specific). Persisted as the `content` of
    a `MemoryCategory.WORKFLOW` memory record (ADR-D4-11) — this model is the content's
    shape/validator, not a store of its own."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claims: ClaimsContext
    conversation_id: str
