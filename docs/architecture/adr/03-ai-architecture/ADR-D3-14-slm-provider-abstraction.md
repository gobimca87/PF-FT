---
id: ADR-D3-14
title: SLM provider abstraction and provider-neutral contract
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Platform Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-13, ADR-D3-15, ADR-D3-17, ADR-D3-18, ADR-D2-01, ADR-D2-13]
source_docs:
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §6, §7, §13, §14, §15, §16, §56, §57, §58, §62, §63, §121, §122, §123"
build_phases: [6]
impacted_paths:
  - src/pf_ft_ai/slm/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-14 — SLM provider abstraction and provider-neutral contract

## 1. Summary

PFF AI will access all language models through a single **provider-neutral SLM
abstraction** — a Python `Protocol` with Pydantic request/response contracts
(15.PF-FT-AI-SLM.md §13–§15) — so that Hugging Face, self-hosted vLLM/TGI, or any future
provider are interchangeable behind one interface. No domain, orchestration or
application code ever imports a provider SDK. This is what makes the ADR-D3-13
migration a configuration change and enables provider/model fallback (ADR-D3-18).

## 2. Context and Problem Statement

15.PF-FT-AI-SLM.md §6 mandates an SLM provider abstraction, §7 lists provider implementations,
§13–§15 fix a provider-neutral request/response contract, and §121–§123 restrict
which models/endpoints are permitted. The layering rule (ADR-D2-01) forbids domain
code importing a provider SDK. Without a formal abstraction, provider specifics
(auth, payload shape, streaming semantics, tool-call format) leak throughout the
codebase, making the ADR-D3-13 self-host migration a rewrite and fallback
impossible. This ADR fixes the shape of that boundary.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | One interface for all providers | 15.PF-FT-AI-SLM.md §6, §15 |
| DR-F-02 | Provider/model fallback support | 15.PF-FT-AI-SLM.md §62–§63; ADR-D3-18 |
| DR-F-03 | Model allowlist + endpoint restriction enforced at the boundary | 15.PF-FT-AI-SLM.md §121–§123 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Provider swap without domain code change | 0 domain edits | 15.PF-FT-AI-SLM.md §15; ADR-D3-13 |
| DR-N-02 | Boundary-typed contracts | Pydantic req/res | CLAUDE.md; 15.PF-FT-AI-SLM.md §13–§14 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Domain code must not import provider SDKs | Architecture | ADR-D2-01 |
| DR-C-02 | Only allowlisted models/endpoints callable | Security | 15.PF-FT-AI-SLM.md §121–§123 |
| DR-C-03 | Contract is a versioned artefact | Organisational | CLAUDE.md |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Providers' capabilities map onto one neutral contract | Add capability flags/adapters | Contract tests per provider |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Provider swappability | 28 | The core purpose | Domain edits to swap |
| EC-02 | Contract clarity & type safety | 18 | Boundary correctness | Pydantic coverage |
| EC-03 | Capability coverage (stream, tools, structured) | 18 | Must not lowest-common-denominator away features | Feature parity |
| EC-04 | Security enforceability (allowlist/endpoint) | 16 | 15.PF-FT-AI-SLM.md §121–§123 | Enforced at boundary |
| EC-05 | Simplicity / maintainability | 12 | Avoid over-abstraction | LOC / concepts |
| EC-06 | Testability (mock provider) | 8 | Deterministic tests | Mock exists |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Thin provider-neutral Protocol + Pydantic contracts + per-provider adapters

**Description.** Define `SLMProvider` protocol (`generate`, `stream`,
`generate_structured`) with neutral Pydantic request/response; each provider is an
adapter translating to/from its SDK; allowlist/endpoint checks live in the
abstraction.
**Strengths.** Clean swap; typed; capability flags avoid lowest-common-denominator;
security enforced centrally; trivial mock provider.
**Weaknesses.** Adapter maintenance per provider.
**Cost / effort.** Low-medium.

### 5.2 Option B — Direct provider SDK calls in application code

**Description.** Call HF/self-host SDKs where needed.
**Strengths.** Least code initially.
**Weaknesses.** Violates ADR-D2-01; swap = rewrite; no central fallback/allowlist.
**Cost / effort.** Low now, high later.

### 5.3 Option C — Adopt a heavyweight LLM framework's provider layer wholesale

**Description.** Depend on a large third-party abstraction (e.g. a broad LLM SDK)
as the provider layer.
**Strengths.** Many providers out of the box.
**Weaknesses.** Large dependency surface; leaks framework types into domain; harder
to enforce allowlist/endpoint policy and our neutral contract; upgrade risk.
**Cost / effort.** Low to start, governance/lock-in cost.

### 5.4 Option D — Gateway/proxy service normalising a single HTTP API (LLM gateway)

**Description.** A network gateway exposing one OpenAI-style API in front of all
providers.
**Strengths.** Language-agnostic; central rate-limit/allowlist; ops-level control.
**Weaknesses.** Extra network hop + service to run; still need a client contract;
overkill for one Python runtime; duplicates APIM/abstraction responsibilities.
**Cost / effort.** Medium ops; useful later at multi-consumer scale.

### 5.5 Option E — Code-generated clients from provider OpenAPI specs

**Description.** Generate typed clients from each provider's OpenAPI.
**Strengths.** Typed; low hand-code.
**Weaknesses.** Generated types are provider-shaped, not neutral → still need a
neutral facade; brittle to provider spec drift.
**Cost / effort.** Medium; doesn't solve neutrality by itself.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No abstraction, single hard-coded provider | DR-F-01/DR-C-01 — blocks the ADR-D3-13 migration |
| Per-workflow bespoke clients | Duplicates the boundary; unmaintainable |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 15.PF-FT-AI-SLM.md §6–§15 and layering
rule ADR-D2-01.

| Criterion | Weight | A: Protocol+adapters | B: Direct SDK | C: Heavy framework | D: Gateway service | E: Codegen clients |
|---|---|---|---|---|---|---|
| EC-01 Swappability | 28 | 5 | 1 | 4 | 5 | 3 |
| EC-02 Contract clarity | 18 | 5 | 2 | 3 | 4 | 4 |
| EC-03 Capability coverage | 18 | 5 | 4 | 4 | 4 | 3 |
| EC-04 Security enforceability | 16 | 5 | 2 | 3 | 5 | 3 |
| EC-05 Simplicity | 12 | 4 | 5 | 2 | 2 | 3 |
| EC-06 Testability | 8 | 5 | 3 | 3 | 3 | 3 |
| **Weighted total** | **100** | **488** | **262** | **342** | **412** | **326** |

Totals (×20): **A = 488**, **D = 412**, **C = 342**, **E = 326**, **B = 262**.

**Sensitivity.** A leads D by 76. D (gateway) becomes attractive only when multiple
independent services/languages consume the SLM — a future scale trigger (RT-01),
at which point a gateway can sit *behind* the same neutral client contract without
changing domain code. A is robust for the current single-runtime design.

## 7. Decision

**PFF AI will implement a thin provider-neutral `SLMProvider` protocol with
Pydantic request/response contracts and per-provider adapters**, enforcing the
model allowlist and endpoint restrictions (15.PF-FT-AI-SLM.md §121–§123) at the boundary and
exposing capability flags so streaming/tool-calling/structured output are not
flattened away. A deterministic mock provider supports testing. Direct SDK use (B)
is forbidden by ADR-D2-01; a heavy framework (C) and codegen (E) are rejected for
leaking provider-shaped types; a gateway service (D) is deferred to a multi-consumer
future.

**Status rationale.** `Accepted` — mandated by 15.PF-FT-AI-SLM.md §6/§15 and ADR-D2-01.

## 8. Architecture Detail

- **Protocol** `src/pf_ft_ai/slm/provider.py`: `generate(req: SLMRequest) ->
  SLMResponse`, `stream(...)`, `generate_structured(..., schema)`; `capabilities()`.
- **Contracts** (15.PF-FT-AI-SLM.md §13–§14): `SLMRequest` (messages, params, model id,
  purpose), `SLMResponse` (text/structured, usage, model+version, finish reason).
- **Adapters**: `HuggingFaceProvider`, later `SelfHostedProvider` (ADR-D5-10).
- **Policy** (15.PF-FT-AI-SLM.md §121–§123): allowlist + endpoint check enforced before any call;
  non-allowlisted model raises `ModelError`.
- **Fallback** (15.PF-FT-AI-SLM.md §62–§63; ADR-D3-18): the abstraction implements ordered
  fallback with logged, non-silent degradation.
- **Config/secrets** (§16): endpoints + `*_secret_ref` (ADR-D5-07).

## 9. Consequences

### 9.1 Positive
- ADR-D3-13 migration is config-only; fallback and allowlist are centralised.
- One place to add tracing, rate-limit, retry (ADR-D3-18) and Langfuse spans.

### 9.2 Negative
- Adapter maintenance per provider; capability flags add minor complexity.

### 9.3 Neutral
- Establishes the pattern reused by the embedding abstraction (ADR-D3-23).

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Direct-SDK brevity | Swappability, security, testability | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Abstraction carries generation only; no business authority |
| Precedence chain | SLM output tier; abstraction never elevates it |
| Four-state separation | Stateless; state lives elsewhere |
| Versioned artefacts | Contract + adapters versioned |
| Adam persona governs *how*, not *what* | Provider invisible to persona |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Lowest-common-denominator loses features | Med | Med | M | Capability flags per provider | ML Eng | Low |
| RSK-02 | Provider SDK leaks past boundary | Low | High | M | Import-linter CI check | AI Arch Lead | Low |
| RSK-03 | Non-allowlisted model called | Low | High | M | Boundary allowlist check + test | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Domain edits to add a provider | 0 | > 0 | Code review | Per provider |
| QM-02 | Non-allowlisted call attempts blocked | 100% | < 100% | Security tests | Per release |
| QM-03 | Contract test parity across providers | 100% | < 100% | CI | Per provider |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Central enforcement point for allowlist/endpoint (reduces surface) |
| Data classification touched | Internal (contract); payloads governed by ADR-D6-07 |
| Personal data / PII | Boundary is where minimisation hooks apply |
| Children's data and safeguarding | N/A at abstraction layer |
| UK GDPR lawful basis and rights impact | Enables enforcing where data may go |
| Audit and evidential requirements | Provider+model+version logged per call |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 |
| Repository paths | `src/pf_ft_ai/slm/` |
| Configuration | Provider config, allowlist, secret refs |
| Contracts / schemas | `SLMRequest`/`SLMResponse` Pydantic models |
| Migration | New adapters implement the protocol |
| Dependencies on other ADRs | ADR-D2-01, ADR-D3-13, ADR-D5-07 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No domain import of a provider SDK | Import-linter |
| AC-02 | Two providers pass the same contract test | CI contract suite |
| AC-03 | Non-allowlisted model raises ModelError | Unit test (§121–§123) |
| AC-04 | Mock provider drives deterministic tests | Test infra |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Per-provider latency/error/usage; Langfuse spans |
| Alerting | Provider errors; allowlist violations |
| Runbook | `docs/runbooks/slm.md` |
| Failure mode and degradation | Provider failure → fallback (ADR-D3-18) |
| Rollback | Config revert |
| Support model impact | ML platform team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Abstraction + adapters | S | negligible | One-time build |
| Per-provider adapter | S each | low | As providers added |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Multiple services/languages need the SLM | Architecture review | Introduce gateway (Option D) behind the contract |
| RT-02 | Provider capabilities diverge sharply | Contract tests | Extend capability flags / adapters |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 |
| Specification sections | 15.PF-FT-AI-SLM.md §6, §7, §13–§16, §56–§58, §62–§63, §121–§123 |
| Requirement IDs | SLM-ABS-* |
| Build phases | 6 |
| Code paths | `src/pf_ft_ai/slm/` |
| Configuration | provider config, allowlist |
| Tests | provider contract suite, mock provider |
| Upstream ADRs | ADR-D2-01, ADR-D3-13 |
| Downstream ADRs | ADR-D3-15, ADR-D3-17, ADR-D3-18, ADR-D3-23 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
