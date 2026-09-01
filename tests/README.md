# Test Suite Layout

Phase 17 (doc 22 — Testing) organizes this repo's tests around the 12-layer pyramid doc
22 §6/§8 defines. Layers with genuinely new Phase 17 content get a dedicated top-level
directory below; layers that already have deep coverage from earlier phases keep living
under `tests/unit/<module>/`, mirroring `src/pff_fa_ai/<module>/` — duplicating that
coverage into empty placeholder directories here would be padding, not testing, so it
was deliberately not done. Every test name is behavior-descriptive
(`test_should_split_erc_into_20_team_batches`-style), per doc 22's convention.

| Layer (doc 22 §6) | Where it lives | Notes |
|---|---|---|
| L1 Unit | `tests/unit/**` | Mirrors `src/pff_fa_ai/**` exactly; one test module per source module. |
| L2 Component | `tests/component/` | Multiple units of one capability exercised together (e.g. ERC batching + aggregation as a pipeline). |
| L3 Contract | `tests/contract/` | Boundary contracts, e.g. the enterprise API status/error space (doc 22 §21). |
| L4 API | `tests/unit/api/` | FastAPI endpoint tests — request/response schema, auth headers, error envelopes. |
| L5 Integration | `tests/unit/integration/` | Tool executor, retry, circuit breaker, idempotency — already integration-level by nature. |
| L6 Agent / Supervisor / Harness | `tests/unit/orchestration/{supervisor,harness,langgraph}/` | No business agent exists yet (`AffiliationAgent` is Phase 23); routing/harness enforcement is tested now, agent-specific behavior arrives with the first real agent. |
| L7 Workflow | *(deferred to Phase 23)* | LangGraph workflow graph tests need a real graph (the affiliation workflow) to test. |
| L8 AI Evaluation | `tests/unit/evaluation/`, `tests/regression/` | Golden dataset harness + retrieval/judge metrics (Phase 16) and the regression runner (Phase 17). |
| L9 Security | `tests/security/`, `tests/adversarial/` | Claims/authorization/secret-handling and prompt-injection/data-exfiltration scenarios, run through the real guardrail pipeline. |
| L10 Performance | `tests/performance/` | Wall-clock regression baselines at large entity counts. |
| L11 End-to-End | `tests/e2e/` | Full conversation journeys through the FastAPI app. The real Club Affiliation E2E scenario is deferred to Phase 23 — see `tests/e2e/README.md`. |
| L12 Production Validation | *(deferred to Phase 19/22)* | Needs a deployed environment and the ops runbook (doc 28) to be meaningful. |

Supporting directories (doc 22 §8, not pyramid layers themselves):

- **`tests/erc/`** — the explicit batching scale-point checklist DEVELOPMENT-GUIDE Phase
  17 calls for (1, 20, 21, 40, 100, 100+ entities), separate from the general-purpose
  edge cases in `tests/unit/context/collection/test_batching.py`.
- **`tests/resilience/`** — cross-dependency isolation under simultaneous failure (doc
  22 §81/§133), on top of the per-component circuit breaker tests already in
  `tests/unit/integration/execution/` and `tests/unit/observability/`.
- **`tests/fixtures/`** — reusable, plain (non-pytest-fixture) factory functions shared
  across every layer above.
- **`tests/mocks/`** — reusable enterprise API `httpx.MockTransport` builders (doc 22
  §101 "Mocking Strategy").
- **`tests/stubs/`** — deterministic large/malformed payload stubs (doc 22 §102 "Stub
  Strategy").
- **`tests/datasets/`** — see its own README; golden datasets live in
  `config/evaluation/golden/`, not duplicated here.
- **`tests/reports/`** — CI-generated test report output only; gitignored, nothing
  committed here (see repo `.gitignore`).

`rag/`, `embeddings/`, `vector/`, `slm/`, `prompts/`, `tools/`, `mcp/`, `service_bus/`,
`memory/`, `cache/`, `session/`, `guardrails/`, `agents/`, `supervisor/`, `harness/`, and
`workflows/` from doc 22 §8's illustrative tree are intentionally **not** created as
separate top-level directories: each of those capabilities already has thorough,
behavior-descriptive unit coverage under the matching `tests/unit/<module>/`
(`tests/unit/domain/session/`, `tests/unit/application/session/`, etc.). The one
exception is MCP, which has no implementation yet at all (see `DEVELOPMENT-GUIDE.md`
§2's deferred decisions) and the business agent catalog, deferred to Phase 23.
