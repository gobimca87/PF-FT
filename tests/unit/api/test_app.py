import pytest
from fastapi.testclient import TestClient

from pf_ft_ai.api import create_app
from pf_ft_ai.api.dependencies import get_workflow_orchestrator
from pf_ft_ai.application.workflows.orchestrator import OrchestrationRequest, OrchestrationResult
from pf_ft_ai.application.workflows.states import OrchestrationStatus

CLAIMS_HEADERS = {"x-subject": "user-1", "x-organization": "club-1"}


class _FakeOrchestrator:
    async def handle_message(self, request: OrchestrationRequest) -> OrchestrationResult:
        return OrchestrationResult(
            status=OrchestrationStatus.COMPLETED, response_message="all done"
        )


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(environment="dev"))


def test_health_should_report_ready_with_configuration_fingerprint(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    assert body["data"]["environment"] == "dev"
    assert len(body["data"]["configuration_hash"]) == 64


def test_create_conversation_should_return_a_new_conversation(client: TestClient) -> None:
    response = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NEW"
    assert body["data"]["conversation_id"].startswith("conv-")


def test_create_conversation_should_require_claims_headers(client: TestClient) -> None:
    response = client.post("/api/v1/conversations")

    assert response.status_code == 422


def test_get_conversation_should_reject_a_different_subject(client: TestClient) -> None:
    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS).json()
    conversation_id = created["data"]["conversation_id"]

    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers={"x-subject": "someone-else", "x-organization": "club-1"},
    )

    assert response.status_code == 400
    assert response.json()["errors"][0]["error_code"] == "ValidationError"


def test_get_conversation_should_404_style_fail_for_unknown_id(client: TestClient) -> None:
    response = client.get("/api/v1/conversations/does-not-exist", headers=CLAIMS_HEADERS)

    assert response.status_code == 409
    assert response.json()["errors"][0]["error_code"] == "WorkflowError"


def test_get_conversation_should_return_it_for_the_owning_subject(client: TestClient) -> None:
    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS).json()
    conversation_id = created["data"]["conversation_id"]

    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=CLAIMS_HEADERS)

    assert response.status_code == 200
    assert response.json()["data"]["conversation_id"] == conversation_id


def test_list_messages_should_return_appended_messages(client: TestClient) -> None:
    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS).json()
    conversation_id = created["data"]["conversation_id"]
    client.post(
        "/api/v1/chat",
        json={"conversation_id": conversation_id, "message": "hi there"},
        headers=CLAIMS_HEADERS,
    )

    response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages", headers=CLAIMS_HEADERS
    )

    assert response.status_code == 200
    contents = [message["content"] for message in response.json()["data"]]
    assert contents[0] == "hi there"  # followed by the orchestrator's honest reply


def test_close_conversation_should_transition_status_to_closed(client: TestClient) -> None:
    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS).json()
    conversation_id = created["data"]["conversation_id"]

    response = client.post(f"/api/v1/conversations/{conversation_id}/close", headers=CLAIMS_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "CLOSED"


def test_chat_should_persist_the_user_message_then_report_no_capability_registered(
    client: TestClient,
) -> None:
    response = client.post("/api/v1/chat", json={"message": "hello there"}, headers=CLAIMS_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FAILED"
    assert "capability registered" in body["message"]


def test_chat_response_should_carry_request_and_correlation_headers(client: TestClient) -> None:
    response = client.post("/api/v1/chat", json={"message": "hello there"}, headers=CLAIMS_HEADERS)

    assert "x-request-id" in response.headers
    assert "x-correlation-id" in response.headers


def test_chat_should_resume_an_existing_conversation(client: TestClient) -> None:
    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS).json()
    conversation_id = created["data"]["conversation_id"]

    response = client.post(
        "/api/v1/chat",
        json={"conversation_id": conversation_id, "message": "continue please"},
        headers=CLAIMS_HEADERS,
    )

    # resolves the existing conversation/session fine; no agent capability registered yet
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


def test_chat_should_return_completed_response_when_orchestrator_succeeds() -> None:
    app = create_app(environment="dev")
    app.dependency_overrides[get_workflow_orchestrator] = lambda: _FakeOrchestrator()
    client = TestClient(app)

    response = client.post("/api/v1/chat", json={"message": "hello"}, headers=CLAIMS_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["data"]["response"] == "all done"


def test_get_session_should_touch_and_return_active_status(client: TestClient) -> None:
    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS).json()
    session_id = created["data"]["session_id"]

    response = client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ACTIVE"
