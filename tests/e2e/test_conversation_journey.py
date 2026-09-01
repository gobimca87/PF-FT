"""doc 22 §94-96 "End-to-End Testing": the real user journey through the deployed
surface — Chat UI → APIM → FastAPI → AI Runtime → back to the caller — exercised as one
coherent multi-step flow rather than the single-endpoint checks
`tests/unit/api/test_app.py` already covers individually. The real Club Affiliation E2E
scenario (doc 22 §95) is deferred to Phase 23, once `AffiliationAgent` exists to drive
it — see `tests/e2e/README.md`."""

from fastapi.testclient import TestClient

from pff_fa_ai.api import create_app

CLAIMS_HEADERS = {"x-subject": "e2e-user", "x-organization": "e2e-club"}


def test_full_conversation_journey_create_chat_resume_list_and_close() -> None:
    client = TestClient(create_app(environment="dev"))

    health = client.get("/api/v1/health")
    assert health.status_code == 200

    created = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS)
    assert created.status_code == 200
    conversation_id = created.json()["data"]["conversation_id"]

    first_turn = client.post(
        "/api/v1/chat",
        json={"conversation_id": conversation_id, "message": "I'd like to affiliate my club"},
        headers=CLAIMS_HEADERS,
    )
    assert first_turn.status_code == 200

    second_turn = client.post(
        "/api/v1/chat",
        json={"conversation_id": conversation_id, "message": "yes, continue"},
        headers=CLAIMS_HEADERS,
    )
    assert second_turn.status_code == 200

    messages = client.get(
        f"/api/v1/conversations/{conversation_id}/messages", headers=CLAIMS_HEADERS
    )
    assert messages.status_code == 200
    contents = [message["content"] for message in messages.json()["data"]]
    assert "I'd like to affiliate my club" in contents
    assert "yes, continue" in contents

    closed = client.post(f"/api/v1/conversations/{conversation_id}/close", headers=CLAIMS_HEADERS)
    assert closed.status_code == 200
    assert closed.json()["status"] == "CLOSED"

    after_close = client.get(f"/api/v1/conversations/{conversation_id}", headers=CLAIMS_HEADERS)
    assert after_close.json()["data"]["status"] == "CLOSED"


def test_journey_should_fail_safely_at_every_untrusted_boundary() -> None:
    """doc 22 §96 "E2E Failure Scenarios" chained together: missing claims, then a
    request against a conversation that was never created."""
    client = TestClient(create_app(environment="dev"))

    missing_claims = client.post("/api/v1/conversations")
    assert missing_claims.status_code == 422

    unknown_conversation = client.get(
        "/api/v1/conversations/does-not-exist", headers=CLAIMS_HEADERS
    )
    assert unknown_conversation.status_code == 409

    cross_subject = client.post("/api/v1/conversations", headers=CLAIMS_HEADERS)
    conversation_id = cross_subject.json()["data"]["conversation_id"]
    stolen_access_attempt = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers={"x-subject": "attacker", "x-organization": "e2e-club"},
    )
    assert stolen_access_attempt.status_code == 400
