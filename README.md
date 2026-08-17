# PFF AI (`pf-ft-ai`)

Conversational orchestration layer for the FA's PFF county/club administration platform.
See [`CLAUDE.md`](CLAUDE.md) for what the project is and the Golden Rule governing it, and
[`DEVELOPMENT-GUIDE.md`](DEVELOPMENT-GUIDE.md) for the full 24-phase build plan and repo
structure. `MD files/` is the read-only specification source of truth — never edit it.

## Status

Phase 0 (repo bootstrap), Phase 1 (configuration & versioning foundation), Phase 2 (state
model & domain layer), Phase 3 (FastAPI runtime + conversation/session layer), Phase 4
(Supervisor, Agent contract, Harness, LangGraph skeleton), Phase 5 (ERC — Enterprise
Runtime Context), Phase 6 (Enterprise Integration — API catalog, Tool Registry, Tool
Executor), Phase 7 (Memory & Cache — Azure Managed Redis), Phase 8 (RAG + Embedding/Vector),
and Phase 9 (SLM Abstraction) complete. Build proceeds phase by phase per
`DEVELOPMENT-GUIDE.md` — later phases assume earlier interfaces exist.

## Enterprise Integration

`src/pf_ft_ai/integration/` implements Phase 6 (doc 10) — genuinely working and end-to-end
tested (via `httpx.MockTransport`, including real retry/circuit-breaker/idempotency
behavior), but with an intentionally **empty** catalog/registry since no real PFF
enterprise API contracts exist yet:

- **`integration/api/`** — `ApiCatalog`/`ApiCatalogEntry` (+ `load_api_catalog()` from
  `config/enterprise/api-catalog/*.yaml`), and `EnterpriseHttpClient` (a port) with a real
  `HttpxEnterpriseHttpClient` implementation — endpoint URLs only ever come from the
  catalog, never from LLM output (doc 10 §80).
- **`integration/tools/`** — `ToolDefinition`/`ToolRegistry` (+ `load_tool_registry()`,
  validated against the API catalog at registration time), `ToolRiskClass`
  (`READ`/`LOW_RISK_WRITE`/`HIGH_RISK_WRITE`/`TRANSACTIONAL`, with `requires_hil()` true
  for the latter two per `DEVELOPMENT-GUIDE.md`), and `ToolExecutor` — the single
  controlled path to enterprise capabilities, implementing the full doc 10 §34 lifecycle
  (`TOOL_REQUESTED → TOOL_RESOLVED → INPUT_VALIDATED → AUTHORIZATION_CHECKED → EXECUTING →
  RESPONSE_RECEIVED → RESPONSE_VALIDATED → RESPONSE_TRANSFORMED → TOOL_COMPLETED`), composed
  from:
  - **`integration/execution/`** — `execute_with_retry()` (exponential backoff + full
    jitter, `max_attempts: 3`/`initial_ms: 250`/`max_ms: 5000`), `CircuitBreaker`
    (`CLOSED → OPEN → HALF_OPEN → CLOSED`), `ConcurrencyLimiter` (bulkhead pools:
    `global_max: 20`, `enterprise.max_parallel: 10`, `mcp.max_parallel: 5`), and
    `InMemoryIdempotencyStore` (key = `workflow_instance_id:operation_id`, reusing Phase 2's
    `IdempotencyStatus`).
  - **`integration/errors/`** — `IntegrationErrorCode` (doc 10 §40) with HTTP-status and
    transport-exception classification, and `is_retryable()`.
- Tools without an explicit `allowed_agents` entry permit **no** agent — deny-by-default,
  not fail-open.
- **MCP is deliberately not built** — `DEVELOPMENT-GUIDE.md` is explicit that MCP is
  selective ("only wire it where explicitly justified"), and no MCP server has been
  identified as needed yet.
- **Enterprise API authentication is token propagation, not stored credentials.** Per the
  Golden Rule, auth is APIM's job, not the AI platform's: the APIM-validated bearer token
  from the Chat UI → FastAPI call is carried on `ClaimsContext.access_token` and forwarded
  unchanged as the `Authorization` header on every enterprise call in `ToolExecutor.execute()`
  (doc 10 §72-74). There is deliberately no `ApiAuthentication`/per-API `credential_secret_ref`
  model — a single propagated token covers every downstream enterprise API.

**Reconciliation note:** `ToolCallStatus` (Phase 2) had the same doc-5-vs-authoritative-doc
issue as Phase 5's `ErcLifecycleStatus` — it was built from doc 5 §30's simplified sketch
before doc 10 §34 (this phase's actual authority) had been read. Corrected to doc 10's
14-value lifecycle here.

`config/enterprise/api-catalog/` and `config/enterprise/tool-registry/` are intentionally
empty (see their READMEs) — real entries arrive with `AffiliationAgent` in Phase 23, once
real PFF API contracts are available to describe truthfully.

## ERC (Enterprise Runtime Context)

`src/pf_ft_ai/context/` implements Phase 5 (doc 8) — the construction *primitives*, built
and fully tested against synthetic data since the enterprise API layer that will actually
feed them doesn't exist until Phase 6:

- **`context/erc/`** — `Erc` entity (+ `ErcSection`, `ErcCompleteness`, `ErcValidationResult`,
  `Freshness`/`compute_freshness`), `Provenance` (system/api/endpoint_ref/retrieved_at/
  authority), the corrected doc-8 12-state `ErcLifecycleStatus` with `assert_valid_transition`
  enforcing the documented state machine, and `ErcAuthority` (`AUTHORITATIVE > DERIVED >
  AI_INTERPRETED > RAG_CONTEXT > USER_PROVIDED`, doc 8 §19).
- **`context/collection/`** — `split_into_batches()`, the batching math verified against the
  spec's own worked examples (103 teams → 6 batches, last = 3; 127 officials → 7 batches,
  last = 7), plus `deduplicate_records()`/`aggregate_records()` for deterministic,
  completeness-aware aggregation (doc 8 §55-58).
- **`context/projection/`** — `compute_available_context_tokens()`, the exact doc 8 §76
  formula (`Available = Model Context Window − System − Agent − Conversation − Reserved
  Output − Safety Margin`).
- Batching (`batch_size: 20`, `max_parallel_batches: 5`, `max_retry_attempts: 2`) and
  context budget (`max_input_tokens: 20000`, `reserved_output_tokens: 4000`,
  `safety_margin_tokens: 1000`) defaults are configuration-driven, matching the doc's own
  numbers exactly, via `load_batching_configuration()` / `load_context_budget_configuration()`
  / `load_erc_configuration()`.

**Reconciliation note:** Phase 2 built `ErcLifecycleStatus` from doc 5's simplified 9-value
sketch before doc 8 (Phase 5's actual authority) had been read in detail. Doc 8's §9-10
lifecycle is more detailed and is what `DEVELOPMENT-GUIDE.md` specifies for this phase, so
the enum was corrected to the 12-value version here — a deliberate fix, not a new
alternative. Rule 4 in `domain/state_consistency.py` was also corrected: `PARTIAL`/`COMPLETE`
are `ErcSectionStatus` values, not `ErcLifecycleStatus` ones (doc 5 §25) — it was
misattributed in Phase 2 and now checks the right enum.

The full ERC *pipeline* (real enterprise API collection → normalization → this
construction logic → context projection into the Agent Harness) wires together once Phase 6
(Enterprise Integration) provides real data sources — these primitives are what it will
be built on.

## Memory & Cache

`src/pf_ft_ai/memory/` and `src/pf_ft_ai/cache/` implement Phase 7 (doc 9), backed by
**Azure Managed Redis** (`docs/adr/0004-memory-cache-store-azure-managed-redis.md` —
RESP-protocol-compatible, so plain `redis.asyncio.Redis` works unmodified). Both packages
are built strictly behind provider-independent interfaces (doc 9 §137-138) — nothing above
`MemoryStore`/`CacheStore` knows Redis exists:

- **`memory/`** — the 10 doc-9 §5 categories (`MemoryCategory`), `MemoryRecord` (doc 9
  §142), `MemoryStore` protocol + `RedisMemoryStore`, and `MemoryService` composing policy +
  store. Write policy (`memory/policy.py`) rejects `AI_INFERENCE` as a write source (doc 9
  §71 — AI inference must never become permanent memory) and resolves TTL from
  `MemorySettings.category_ttl_seconds`. ERC is referenced (`erc_id` + `version` +
  `workflow_instance_id`), **never** copied in full (doc 9 §16-17).
- **`cache/`** — the 10 doc-9 §33 categories (`CacheCategory`), `build_cache_key()`
  including tenant + organization + resource + operation + parameters + version (doc 9
  §36-37), `assert_cacheable_method()` refusing to cache `POST`/`PUT`/`PATCH`/`DELETE` (doc
  9 §35), `CacheStore` protocol + `RedisCacheStore` (including targeted, prefix-based
  `invalidate()` per doc 9 §115), and `CacheService.get_or_set()` implementing the
  cache-aside pattern (doc 9 §41).
- Both key layouts are scope-isolated (`pf-ft:<environment>:memory:...` /
  `pf-ft:<environment>:cache:...`, then tenant/user/org/conversation/workflow) so dev/test
  data can never collide with prod, and one tenant can never read another's entries (doc 9
  §77, §99-101).
- Redis connection config (`load_redis_configuration()`) is Key Vault-ready: `dev`/`test`/
  `uat` point at local Redis; `staging`/`prod` ship obvious placeholder hosts plus
  `password_secret_ref: AZURE_REDIS_PASSWORD`, so the app fails fast with `ConfigurationError`
  until the real Key Vault-backed secret is supplied — it can never silently fall back to a
  dev endpoint.
- Not yet wired into the FastAPI app/agent harness — that lands when the Context Builder
  (doc 9 §148) is built, consuming `MemoryService`/`CacheService` alongside ERC.

## RAG + Embedding/Vector

`src/pf_ft_ai/embedding_vector/` and `src/pf_ft_ai/rag/` implement Phase 8 (docs 13, 14).
The vector/search-engine technology is still an open ADR
(`docs/adr/0003-deferred-decisions-log.md`), so — same discipline as Phase 7 before Redis
was resolved — everything is built strictly behind interfaces with genuinely working
in-memory implementations, not stubs:

- **`embedding_vector/`** — `EmbeddingProvider` protocol (`MockEmbeddingProvider`,
  deterministic and hash-based; `HuggingFaceEmbeddingProvider`, real, doc 14 §11's initial
  provider), `EmbeddingModelRegistry` enforcing dimension validation *before* indexing or
  search (doc 14 §18-19), `VectorStore` protocol + `InMemoryVectorStore` (real cosine-
  similarity search, tenant/organization/domain-filtered before results ever leave the
  store — doc 14 §49, §125), and `IndexAliasRegistry` for blue/green index switching (doc
  14 §77-78).
- **`rag/`** — `route_information_requirement()` implementing the doc 13 §5 decision
  boundary (`CURRENT_TRANSACTIONAL`/`CURRENT_AUTHORITATIVE` → Enterprise API, never RAG;
  reference/policy/documentary/historical/procedural → RAG), `chunk_text()` (target/overlap
  token chunking, doc 13 §41-42), `IngestionPipeline` (Source → Chunking → Metadata →
  Embedding → Vector Index) and `RagService` (Query → ACL/tenant filter *before* search →
  hybrid vector+keyword retrieval → Reciprocal Rank Fusion → rerank → citations), plus a
  `TermOverlapKeywordSearch` — an honest term-overlap scorer, not a stand-in claiming to be
  BM25 or a real search engine, since that technology is equally undecided.
- Every retrieved chunk carries citation metadata (`document_id`, `document_version`,
  `title`, `page`, `section`, `chunk_id`) built strictly from the chunk that was actually
  retrieved (`rag/citations.py`) — there is no path to inventing a citation.
- No specific embedding/SLM model has been evaluation-selected yet (doc 14 §13: "model
  selection must be evaluation-driven"), so `provider: mock` is the current configuration
  for both embedding and SLM (`config/base/embedding.yaml`) — not a stand-in for a real
  decision, an honest placeholder until an evaluation exercise picks one.
- Defaults (`config/base/rag.yaml`): `chunking.target_tokens: 400` /
  `overlap_tokens: 50`, `retrieval.vector_top_k: 20` / `keyword_top_k: 20`,
  `reranking.top_n: 8`, `agentic_rag.max_iterations: 2` (the value is configured; the
  iterative retrieve-evaluate loop itself is not built yet — that's Context Builder/Agent
  Harness integration work for a later phase).
- Query rewriting/expansion (doc 13 §57-58) needs the SLM and is deliberately not built
  here.
- Not yet wired into the FastAPI app/agent harness — same status as Phase 7's Memory/Cache,
  pending the Context Builder phase.

## SLM Abstraction

`src/pf_ft_ai/slm/` implements Phase 9 (doc 15). Request/response contracts
(`SlmRequest`/`SlmResponse`) follow the doc's exact fields (`model_id, messages,
temperature, top_p, max_output_tokens, stream, response_format` /
`request_id, model_id, model_version, output, usage, finish_reason`):

- `SLMProvider` protocol (`generate`/`stream`/`health`) with `MockSLMProvider`
  (deterministic, required for reproducible tests) and `HuggingFaceSLMProvider` (real, via
  `httpx`, tested with `httpx.MockTransport`).
- `SlmService` wraps a provider with retry (transient-only, exponential backoff+jitter) and
  a circuit breaker — reusing the exact generic `execute_with_retry()`/`CircuitBreaker`
  primitives Phase 6 built for enterprise integration (doc 10 §41-44, §90), since they're
  provider-agnostic algorithms, not integration-specific logic. Fallback to an approved
  model is **never silent**: `SlmExecutionResult.status` always tells the caller whether
  the primary or the fallback served the response (`SlmStatus.SUCCEEDED` vs. `FALLBACK`),
  and with no fallback configured a primary failure raises `ModelError` rather than
  guessing.
- `assert_pinned_model_version()` rejects `model_version: "latest"` in `prod` — production
  must pin an explicit version (doc 15).
- No agent code should ever import a concrete provider directly — only `SLMProvider`.

## Running the API

```bash
uvicorn pf_ft_ai.api:create_app --factory --reload
```

`GET /api/v1/health`, `POST/GET /api/v1/conversations`, `GET
/api/v1/conversations/{id}/messages`, `POST /api/v1/conversations/{id}/close`, `GET
/api/v1/sessions/{id}` all work end-to-end today (in-memory `ConversationRepository` /
`SessionRepository` / `MessageRepository` — concrete store is still an open ADR, see
below). `POST /api/v1/chat` now runs the full request lifecycle for real: it
resolves/creates the conversation and session, persists the user message, and calls
`SupervisorWorkflowOrchestrator` — which routes through `Supervisor` → `AgentRegistry` →
`AgentHarness`. The `AgentRegistry` is genuinely empty today (no business agents exist
until `AffiliationAgent` lands in Phase 23), and the default `UnknownIntentClassifier`
honestly reports zero-confidence "unknown" intent (no SLM-based NLU until Phase 9/10) — so
`/chat` returns a normal `200` with `status: "FAILED"` and a message explaining no
capability is registered yet, rather than fabricating a response or an internal error.

Claims are read from `x-subject` / `x-organization` / `x-roles` headers (the trust
boundary is APIM in production — these are pre-validated claims forwarded as headers, per
CLAUDE.md's Golden Rule that the AI platform never authenticates/authorizes itself).

## Agentic orchestration skeleton

`src/pf_ft_ai/orchestration/` implements Phase 4 (doc 7):

- **Supervisor** (`orchestration/supervisor/`) — `IntentClassifier` port (+ the honest
  `UnknownIntentClassifier` default), `AgentRegistry` (routing capability + optional
  executor per agent), and `Supervisor.route()` producing a schema-validated
  `SupervisorDecision` (`ROUTED` / `CLARIFICATION_REQUIRED` / `ROUTING_FAILED`).
- **Agent contract** (`agents/`) — the `Agent` protocol (`execute(context) -> result`),
  `AgentExecutionContext`, `AgentExecutionResult` (doc 7 §17-19).
- **Agent Harness** (`orchestration/harness/`) — the controlled boundary every agent runs
  inside: claims-presence gate, `max_execution_time_seconds` timeout, and bounded retry on
  transient `IntegrationError`s up to `max_retry_count`. The remaining harness
  responsibilities (ERC/memory/tools/RAG/SLM/guardrail provider composition, doc 7 §171)
  wire in as each of those phases lands.
- **LangGraph skeleton** (`orchestration/langgraph/`) — the typed `GraphState` TypedDict,
  a `NodeRegistry` pre-seeded with doc 7 §28-29's full node catalog classified
  deterministic vs. AI-assisted, and `build_skeleton_graph()` — a real `langgraph`
  `StateGraph` demonstrating explicit loop termination (either a node signals completion,
  or `max_graph_steps` is hit) that Phase 23's `AffiliationAgent` graph extends with real
  business nodes.
- Runtime limits (`max_graph_steps`, `max_agent_loops`, `max_tool_calls`,
  `max_parallel_calls`, `max_context_tokens`, `max_output_tokens`,
  `max_execution_time_seconds`, `max_retry_count`, `max_batch_size`) are
  configuration-driven via `load_harness_configuration()`, same pattern as platform/
  conversation config.

## State model & domain layer

`src/pf_ft_ai/domain/` holds the framework-free domain layer: `Conversation`, `Session`,
and `WorkflowInstance` entities (all immutable/frozen — a transition is a new version via
`model_copy`), the `Versioned` mixin + `assert_expected_version` for optimistic
concurrency, `StateTransition`/`StateActor` for auditable transitions, the generic
`StateRepository` protocol (`create/get/update/checkpoint/transition/resume/cancel`), and
the 7 mandatory state-consistency rules from doc 5 §50 (`domain/state_consistency.py`).

Every other state category from doc 5 (Supervisor, Agent, Graph, ERC, Tool, RAG, SLM,
Event, Cache, idempotency) has its enum defined now in its eventual owning package
(e.g. `orchestration/supervisor/states.py`, `context/erc/states.py`, `rag/states.py`) —
just the vocabulary; the capability logic for each arrives in that package's own phase.

## Configuration

`src/pf_ft_ai/configuration/` loads `config/base/platform.yaml` merged with
`config/environments/<env>/platform.yaml` (environment overrides win), resolves any
`*_secret_ref` keys through a `SecretResolver` (env vars locally; Key Vault-backed
resolver arrives with the Azure integration phase), validates the result against
Pydantic models, and returns an immutable `PlatformConfiguration` with a SHA-256
`configuration_hash` for drift detection. Invalid or missing mandatory configuration
raises `ConfigurationError` — the app is meant to fail fast rather than start in a bad
state (doc 17 §21).

```python
from pf_ft_ai.configuration import load_platform_configuration

config = load_platform_configuration("dev")
```

Release manifests (`config/releases/<version>.yaml`) are loaded via
`load_release_manifest("0.1.0")` and describe exactly what shipped in a release —
components are added as later phases produce versioned artifacts (agents, prompts,
models, ...).

## Decisions already made

- Python `>=3.11,<3.13`, type checker **mypy** (strict) — see
  [`docs/adr/0002-python-version-and-type-checker.md`](docs/adr/0002-python-version-and-type-checker.md).
- Environment stage model: `DEV → TEST → UAT → STAGE → PROD`.
- First (and for now only) production agent: `AffiliationAgent`.
- Memory/cache store: **Azure Managed Redis** — see
  [`docs/adr/0004-memory-cache-store-azure-managed-redis.md`](docs/adr/0004-memory-cache-store-azure-managed-redis.md).
- Still-open decisions (vector store, IaC tool, manifest tool, deployment strategy) are
  tracked and resolved as their phase is reached — see
  [`docs/adr/0003-deferred-decisions-log.md`](docs/adr/0003-deferred-decisions-log.md).

## Local setup

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows; use .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"
pre-commit install
cp .env.example .env            # fill in local values; never commit .env
```

## Common tasks

```bash
ruff check .                    # lint
ruff format .                   # format
mypy src                        # type check
pytest                          # tests + coverage
pre-commit run --all-files      # everything pre-commit will run in CI
```

## Branching

`main`, `develop`, `feature/*`, `bugfix/*`, `hotfix/*`, `release/*`. Commits follow
Conventional Commits (`feat(agent): ...`, `fix(erc): ...`, `test(rag): ...`) — see
`CLAUDE.md` → Coding Conventions.

## Repository layout

Canonical package: `src/pf_ft_ai/`. Full annotated tree (which spec doc governs which
folder) is in `DEVELOPMENT-GUIDE.md` §3.
