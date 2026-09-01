from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Depends, Header, Request

from pff_fa_ai.agents.affiliation import (
    AffiliationAgent,
    AffiliationDependencies,
    build_affiliation_dependencies,
)
from pff_fa_ai.agents.affiliation.classifier import AffiliationIntentClassifier
from pff_fa_ai.application.conversation.service import ConversationService
from pff_fa_ai.application.session.service import SessionService
from pff_fa_ai.application.workflows.orchestrator import WorkflowOrchestrator
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.configuration.loader import (
    load_conversation_configuration,
    load_harness_configuration,
    load_platform_configuration,
)
from pff_fa_ai.configuration.models import (
    ConversationConfiguration,
    Environment,
    HarnessLimits,
    PlatformConfiguration,
)
from pff_fa_ai.infrastructure.persistence import (
    InMemoryConversationRepository,
    InMemoryMessageRepository,
    InMemorySessionRepository,
    InMemoryWorkflowRepository,
)
from pff_fa_ai.orchestration.harness import AgentHarness
from pff_fa_ai.orchestration.supervisor import AgentRegistry, Supervisor
from pff_fa_ai.orchestration.supervisor.classifier import IntentClassifier
from pff_fa_ai.orchestration.supervisor.models import AgentCapability
from pff_fa_ai.orchestration.workflow_orchestrator import SupervisorWorkflowOrchestrator

AFFILIATION_AGENT_ID = "affiliation_agent"
AFFILIATION_AGENT_VERSION = "1.0.0"


@dataclass
class AppState:
    environment: Environment
    platform_configuration: PlatformConfiguration
    conversation_configuration: ConversationConfiguration
    harness_limits: HarnessLimits
    affiliation_dependencies: AffiliationDependencies
    conversation_repository: InMemoryConversationRepository = field(
        default_factory=InMemoryConversationRepository
    )
    message_repository: InMemoryMessageRepository = field(default_factory=InMemoryMessageRepository)
    session_repository: InMemorySessionRepository = field(default_factory=InMemorySessionRepository)
    agent_registry: AgentRegistry = field(default_factory=AgentRegistry)
    intent_classifier: IntentClassifier = field(default_factory=AffiliationIntentClassifier)
    workflow_orchestrator: WorkflowOrchestrator = field(init=False)

    def __post_init__(self) -> None:
        # doc 4 §72 / DEVELOPMENT-GUIDE Phase 23: `AffiliationAgent` is the platform's
        # first (and currently only) registered business agent — the rest of the
        # catalog stays deferred to a real product decision
        # (docs/adr/0003-deferred-decisions-log.md).
        self.agent_registry.register(
            AgentCapability(
                agent_id=AFFILIATION_AGENT_ID,
                agent_version=AFFILIATION_AGENT_VERSION,
                workflow="club-affiliation",
                supported_intents=self.affiliation_dependencies.settings.supported_intents,
            ),
            executor=AffiliationAgent(self.affiliation_dependencies),
        )
        supervisor = Supervisor(self.agent_registry, self.intent_classifier)
        harness = AgentHarness(self.harness_limits)
        self.workflow_orchestrator = SupervisorWorkflowOrchestrator(
            supervisor, harness, self.agent_registry
        )


def build_app_state(*, environment: Environment = "dev") -> AppState:
    affiliation_dependencies = build_affiliation_dependencies(
        environment=environment, workflow_repository=InMemoryWorkflowRepository()
    )
    return AppState(
        environment=environment,
        platform_configuration=load_platform_configuration(environment),
        conversation_configuration=load_conversation_configuration(environment),
        harness_limits=load_harness_configuration(environment).harness,
        affiliation_dependencies=affiliation_dependencies,
    )


def get_app_state(request: Request) -> AppState:
    app_state: AppState = request.app.state.app_state
    return app_state


def get_conversation_service(state: AppState = Depends(get_app_state)) -> ConversationService:
    return ConversationService(
        state.conversation_repository,
        state.message_repository,
        state.conversation_configuration.conversation,
        state.conversation_configuration.security,
    )


def get_session_service(state: AppState = Depends(get_app_state)) -> SessionService:
    return SessionService(state.session_repository, state.conversation_configuration.session)


def get_workflow_orchestrator(state: AppState = Depends(get_app_state)) -> WorkflowOrchestrator:
    return state.workflow_orchestrator


def _extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None
    prefix = "Bearer "
    return authorization[len(prefix) :] if authorization.startswith(prefix) else authorization


def get_claims_context(
    x_subject: str = Header(...),
    x_organization: str = Header(...),
    x_roles: str = Header(default=""),
    authorization: str | None = Header(default=None),
) -> ClaimsContext:
    roles = tuple(role.strip() for role in x_roles.split(",") if role.strip())
    return ClaimsContext(
        subject=x_subject,
        organization=x_organization,
        roles=roles,
        access_token=_extract_bearer_token(authorization),
    )


def get_correlation_ids(request: Request) -> tuple[str, str]:
    return request.state.request_id, request.state.correlation_id
