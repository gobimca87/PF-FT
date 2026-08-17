from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Depends, Header, Request

from pf_ft_ai.application.conversation.service import ConversationService
from pf_ft_ai.application.session.service import SessionService
from pf_ft_ai.application.workflows.orchestrator import WorkflowOrchestrator
from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.configuration.loader import (
    load_conversation_configuration,
    load_harness_configuration,
    load_platform_configuration,
)
from pf_ft_ai.configuration.models import (
    ConversationConfiguration,
    Environment,
    HarnessLimits,
    PlatformConfiguration,
)
from pf_ft_ai.infrastructure.persistence import (
    InMemoryConversationRepository,
    InMemoryMessageRepository,
    InMemorySessionRepository,
)
from pf_ft_ai.orchestration.harness import AgentHarness
from pf_ft_ai.orchestration.supervisor import AgentRegistry, Supervisor, UnknownIntentClassifier
from pf_ft_ai.orchestration.workflow_orchestrator import SupervisorWorkflowOrchestrator


@dataclass
class AppState:
    environment: Environment
    platform_configuration: PlatformConfiguration
    conversation_configuration: ConversationConfiguration
    harness_limits: HarnessLimits
    conversation_repository: InMemoryConversationRepository = field(
        default_factory=InMemoryConversationRepository
    )
    message_repository: InMemoryMessageRepository = field(default_factory=InMemoryMessageRepository)
    session_repository: InMemorySessionRepository = field(default_factory=InMemorySessionRepository)
    agent_registry: AgentRegistry = field(default_factory=AgentRegistry)
    workflow_orchestrator: WorkflowOrchestrator = field(init=False)

    def __post_init__(self) -> None:
        supervisor = Supervisor(self.agent_registry, UnknownIntentClassifier())
        harness = AgentHarness(self.harness_limits)
        self.workflow_orchestrator = SupervisorWorkflowOrchestrator(
            supervisor, harness, self.agent_registry
        )


def build_app_state(*, environment: Environment = "dev") -> AppState:
    return AppState(
        environment=environment,
        platform_configuration=load_platform_configuration(environment),
        conversation_configuration=load_conversation_configuration(environment),
        harness_limits=load_harness_configuration(environment).harness,
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
