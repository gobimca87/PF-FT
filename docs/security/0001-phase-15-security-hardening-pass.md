# Phase 15 — Security Hardening Pass

Date: 2026-08-17
Doc: 19 (`MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md`)

## Status

Complete for the codebase as it exists through Phase 14. This is a review/audit
deliverable, not a new-code phase — findings below are evidence-based (file:line
references), not assumptions. Re-run this pass whenever a new capability is wired into
the live request path, and definitely before Phase 23 (`AffiliationAgent`, the first
phase where a real end-to-end request actually flows through the whole chain).

## 1. Trust-zone walk-through (doc 19 §6-7)

Doc 19's 9 zones, mapped to what exists today:

| Zone | Boundary | Status |
|---|---|---|
| ZONE-1 User/External | Chat UI → APIM | Outside this codebase (enterprise-owned) |
| ZONE-2 Enterprise API Gateway | APIM → FastAPI | AI platform never authenticates/authorizes — `api/dependencies.py get_claims_context()` only *reads* pre-validated `x-subject`/`x-organization`/`x-roles`/`Authorization` headers, never validates them itself. Correct per the Golden Rule. |
| ZONE-3 AI Application | FastAPI → LangGraph | `api/app.py` middleware stamps `request_id`/`correlation_id` before any handler runs. `ClaimsContext` frozen at construction (§2 below). |
| ZONE-4 AI Runtime | Supervisor → Agent → Harness | `AgentHarness.execute()` (`orchestration/harness/harness.py:19`) refuses to run without `context.claims.subject`. Tool allowlist is deny-by-default (`ToolRegistry.is_agent_allowed`, doc 10 §Phase 6). |
| ZONE-5 Enterprise Services | Tool Executor → Enterprise API | `ToolExecutor.execute()` propagates the APIM-validated bearer token unchanged (`integration/tools/executor.py:128-132`) — no stored per-API credential exists to leak. |
| ZONE-6 Data/RAG | RAG retrieval, Memory, Cache | Tenant isolation enforced at the store layer (`InMemoryVectorStore`/`RedisMemoryStore`/`RedisCacheStore` all filter by `tenant_id` before returning results — verified by dedicated cross-tenant tests in each package). |
| ZONE-7 Model Provider | SLM/Embedding | `ModelAllowlistPolicy` (`guardrails/model_policy.py`) BLOCKs unapproved `model_id`s; `assert_pinned_model_version()` (`slm/versioning.py`) rejects `"latest"` in `prod`. |
| ZONE-8 Observability | Langfuse | Fails open by design (doc 19 doesn't require it fail closed) — `LangfuseObservabilityClient` swallows every SDK exception (Phase 14), so a compromised/unavailable Langfuse endpoint can't take down core execution, but also can't be used as a security control. |
| ZONE-9 Management/CI-CD | Pre-commit, (future) CI | `detect-secrets` + `ruff` (bandit-derived `S` rules) run via `.pre-commit-config.yaml` today; no `.github/workflows/` CI exists yet (see §4). |

**Zero-trust principle (doc 19 §8)** — spot-checked against the six explicit claims:

- "No tool is trusted automatically" — `ToolExecutor` checks `is_agent_allowed()` +
  required claims before every call. ✅
- "No model output is trusted automatically" — output schema validation exists at the
  guardrail layer (`guardrails/pii.py`, `guardrails/secrets.py`) but is **not yet wired**
  into any live SLM response path, because no live path exists (Phase 23). ⚠️ tracked gap.
- "No retrieved document is trusted automatically" — `guardrails/content.py
  wrap_rag_evidence()` labels RAG content `CONTROLLED_CONTEXT` and wraps it as
  non-instructional data; `PromptComposer`'s exact-match trust check (Phase 10) would
  reject it if mislabeled as `TRUSTED`. Mechanism is real and tested; **not yet wired**
  into a live prompt-assembly call for the same reason as above.
- "No MCP response is trusted automatically" — N/A, MCP is deliberately not built
  (doc 10 explicit: "selective, only wire where justified"; no server identified yet).
- "No event payload is trusted automatically" — `messaging/events/validator.py
  validate_envelope()` enforces a source allowlist; `messaging/guardrails/content.py`-style
  wrapping isn't needed since events never reach a prompt directly today.

## 2. Authorization context immutability (doc 19 §13)

Verified directly in source, not assumed:

```
src/pf_ft_ai/common/claims.py:9        ClaimsContext        ConfigDict(frozen=True)
src/pf_ft_ai/agents/context.py:10      AgentExecutionContext ConfigDict(frozen=True)
src/pf_ft_ai/guardrails/models.py:26   GuardrailContext      ConfigDict(frozen=True, extra="forbid")
src/pf_ft_ai/messaging/events/models.py EventEnvelope        ConfigDict(frozen=True, extra="forbid")
```

- `get_claims_context()` (`api/dependencies.py`) builds `ClaimsContext` **only** from
  request headers — there is no code path where a user message, tool result, or model
  output can set `subject`/`roles`/`permissions`/`organization`.
- Pydantic frozen models raise on any attribute assignment attempt; every "update" in this
  codebase is a `model_copy(update={...})` producing a *new* object, never in-place
  mutation of claims (spot-checked: `InMemorySessionRepository`, `InMemoryWorkflowRepository`
  transition methods copy the *entity*, never touch the claims that authorized the call).
- **Not model-editable**: the SLM abstraction (`slm/models.py SlmRequest`) has no field
  through which a model response could feed back into `ClaimsContext` construction.

Confirmed: authorization context is immutable and non-model-editable at every layer that
exists today. ✅

## 3. AI threat category checklist (doc 19 §125, DEVELOPMENT-GUIDE Phase 15's 10)

| Threat | Primitive(s) built | Wired into a live path? |
|---|---|---|
| Prompt Injection | `guardrails/content.py` wrapping, `PromptComposer` exact-match trust guardrail (Phase 10-11) | Not yet — no live agent calls the composer end-to-end |
| Jailbreak | Trust hierarchy (`guardrails/trust.py assert_no_privilege_escalation`) | Not yet, same reason |
| Sensitive Info Disclosure | `PiiDetectionPolicy`, `SecretDetectionPolicy` (regex-based, Phase 11) | Not yet — no output path calls them |
| Excessive Agency | Tool allowlist (deny-by-default, Phase 6), `AuthorizationContextPolicy` (Phase 11) | **Yes** — `ToolExecutor` enforces this on every call today |
| System Prompt Leakage | System-prompt content marked `TRUSTED`/`PLATFORM_SYSTEM`, never echoed into `DATA_CONTEXT` | Structural (composer never places system content where it could leak back), not runtime-tested against a real SLM yet |
| Vector/RAG Weakness | Tenant-isolated `InMemoryVectorStore`, `SourceAuthorityLevel` classification exists on `SourceRegistration` | ⚠️ **Gap**: `rag/pipeline.py IngestionPipeline` does not check `authority_level` before ingesting — an `UNTRUSTED`-classified source isn't currently rejected at ingestion time |
| Tool/MCP Abuse | Tool allowlist, parameter schema validation, HIL required for `HIGH_RISK_WRITE`/`TRANSACTIONAL` | **Yes** for tools; MCP N/A (not built) |
| Model Supply Chain | `ModelAllowlistPolicy`, pinned-version guard | **Yes** — both are real, tested guardrails, not yet invoked by a live call path |
| Model Denial of Service | Circuit breaker per-dependency (`ResilienceRegistry`, Phase 14), retry budgets | ⚠️ **Gap**: no `ConcurrencyLimiter`/bulkhead exists for SLM calls specifically (Phase 6 built one for enterprise API/tool calls only) |
| Data Poisoning | Same `SourceAuthorityLevel` gap as RAG Weakness above | ⚠️ Same tracked gap |

**Overarching finding, stated plainly**: this codebase has built extensive, genuinely
tested security *mechanisms* (guardrail pipeline, trust classification, tool allowlists,
model allowlists, tenant isolation) but most of them are not yet wired into a live
request path, because no live path exists — every phase since Phase 7 has explicitly
deferred "wiring into X" until Phase 23 (`AffiliationAgent`) gives the platform its first
real agent to wire around. That is a scope/sequencing fact, not a hidden defect, and it's
consistent with every prior phase's README section — but it means **Phase 15 cannot
certify runtime security of a request path that doesn't exist yet**. What it can and does
certify: every primitive built so far is individually correct, tested, and ready to be
wired in Phase 23 without redesign.

## 4. CI security gates (doc 19, DEVELOPMENT-GUIDE Phase 15's 4th bullet)

Already wired (pre-commit, local + would run in any future CI that invokes it):

- **Secret scan** — `detect-secrets` (`.pre-commit-config.yaml`, `.secrets.baseline`).
- **SAST (lightweight)** — `ruff` with the `S` (flake8-bandit) ruleset selected
  (`pyproject.toml [tool.ruff.lint] select`).

Added this phase — `.github/workflows/security.yml`: a **standalone** security-gate
workflow (SAST via `ruff check`, dependency scan via `pip-audit`, secret scan via
`detect-secrets`) that runs on every push/PR. Deliberately scoped to only what's
feasible today:

- **Not included**: container scan (no Dockerfile/container build exists yet), IaC scan
  (no IaC tool has been chosen — `docs/adr/0003-deferred-decisions-log.md`), config scan
  and prompt security scan (no dedicated scanner chosen yet).
- This workflow is intentionally independent of the full build/test/deploy pipeline
  DEVELOPMENT-GUIDE assigns to Phase 19 — it can be merged into that pipeline unchanged
  when Phase 19 is reached ("feeds into Phase 19 CI/CD" per the guide).

**Update, Phase 19:** `security.yml` has been superseded. Its three jobs (SAST,
dependency scan, secret scan) now run unchanged as steps inside
`.github/workflows/ci.yml`'s full pipeline, exactly as anticipated above — the
standalone file was removed rather than left running redundantly alongside it.

## 5. Summary of new findings from this pass

1. **Gap** — `rag/pipeline.py IngestionPipeline` doesn't check `SourceRegistration.
   authority_level` before ingesting; an `UNTRUSTED` source can currently be ingested.
   Recommend enforcing this before Phase 23's real ingestion begins.
2. **Gap** — no concurrency bulkhead exists for SLM calls (`SlmService` has retry +
   circuit breaker but no `ConcurrencyLimiter`), leaving a Model-DoS-via-flooding path
   theoretically open once a live path exists.
3. **Not a gap, a sequencing fact** — the guardrail pipeline, prompt composer trust
   checks, and content-wrapping functions are real and tested but not yet invoked by any
   live request path, because none exists until Phase 23.

Items 1-2 are small, targeted fixes appropriate to make when `IngestionPipeline` and
`SlmService` are next touched (e.g. during Phase 23 wiring) rather than as isolated
changes now, to avoid churn ahead of the real integration work.
