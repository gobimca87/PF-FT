from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.orchestration.supervisor.states import SupervisorStatus


class IntentClassification(BaseModel):
    model_config = ConfigDict(frozen=True)

    intent: str
    confidence: float = Field(ge=0.0, le=1.0)


class AgentCapability(BaseModel):
    """Routing-relevant registry entry (doc 7 §22-23) — execution wiring is separate."""

    model_config = ConfigDict(frozen=True)

    agent_id: str
    agent_version: str
    workflow: str
    supported_intents: tuple[str, ...]
    enabled: bool = True


class SupervisorDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: SupervisorStatus
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    clarification_required: bool
    agent_id: str | None = None
    workflow: str | None = None
