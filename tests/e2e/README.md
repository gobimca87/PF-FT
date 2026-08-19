# End-to-End Tests

`test_conversation_journey.py` exercises the full request boundary this platform can
reach today: Chat UI → APIM (simulated via claims headers) → FastAPI → AI Runtime →
back to the caller, as one coherent conversation lifecycle (create → chat → resume →
list → close) plus the chained failure scenarios doc 22 §96 calls for.

The real **Club Affiliation** E2E scenario (doc 22 §95 — user requests affiliation →
teams/officials/courses processed → ERC built → response generated → portal/workflow
links returned) is **not built here**. It requires `AffiliationAgent`, which
DEVELOPMENT-GUIDE.md schedules for Phase 23 — until that agent exists there is no real
capability registered for the orchestrator to route to (see
`test_chat_should_persist_the_user_message_then_report_no_capability_registered` in
`tests/unit/api/test_app.py`). This directory gets its first real business-workflow E2E
test once Phase 23 lands.
