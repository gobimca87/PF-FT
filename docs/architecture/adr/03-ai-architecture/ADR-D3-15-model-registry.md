---
id: ADR-D3-15
title: Model registry — capability, purpose and status model
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Release Manager]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-13, ADR-D3-14, ADR-D3-16, ADR-D3-18, ADR-D5-06, ADR-D6-15]
source_docs:
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §8, §9, §10, §11, §12, §56, §58, §83, §151, §152, §153, §154, §155"
  - "MD files/4 AI/14.PF-FT-AI-EMBEDDING-VECTOR.md §15, §16"
build_phases: [6]
impacted_paths:
  - src/pf_ft_ai/slm/registry/
  - config/models/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-15 — Model registry — capability, purpose and status model

## 1. Summary

PFF AI will maintain a **declarative model registry** (config-as-code, Git-versioned)
that records every language and embedding model by `id@version` with its
**capabilities**, **purpose/task class**, **status** lifecycle (ACTIVE/TESTING/
DEPRECATED/RETIRED/BLOCKED) and compatibility metadata (15.PF-FT-AI-SLM.md §8–§12, §154–§155;
14.PF-FT-AI-EMBEDDING-VECTOR.md §15–§16). Model routing (ADR-D3-16), fallback (ADR-D3-18) and provider
selection (ADR-D3-14) all read from this single registry; no model is callable
unless it is registered and ACTIVE.

## 2. Context and Problem Statement

15.PF-FT-AI-SLM.md §8–§12 define a model registry with responsibilities, status, capability and
purpose; §151–§155 cover promotion, release artefact and immutable production
versions; 14.PF-FT-AI-EMBEDDING-VECTOR.md §15–§16 mirror this for embeddings. Without a formal registry,
model choice is scattered across code and config, routing/fallback cannot reason
about capabilities, and there is no controlled promotion or allowlist. This ADR
fixes what the registry is, where it lives, and how it is versioned.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Resolve model by id@version with capability+purpose | 15.PF-FT-AI-SLM.md §8–§12 |
| DR-F-02 | Drive routing and fallback from declared capabilities | 15.PF-FT-AI-SLM.md §56, §58; ADR-D3-16/18 |
| DR-F-03 | Status lifecycle gates which models are usable | 15.PF-FT-AI-SLM.md §10 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Immutable production model versions | No in-place edit | 15.PF-FT-AI-SLM.md §155 |
| DR-N-02 | Auditable promotion | Versioned change history | 15.PF-FT-AI-SLM.md §151–§152 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Registry is a versioned artefact | Organisational | CLAUDE.md; 15.PF-FT-AI-SLM.md §154 |
| DR-C-02 | Only registered+ACTIVE models callable (allowlist) | Security | 15.PF-FT-AI-SLM.md §121; ADR-D3-14 |
| DR-C-03 | Same model+version for doc & query embeddings | Platform | 14.PF-FT-AI-EMBEDDING-VECTOR.md §7; ADR-D3-23 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Declarative config suffices (no runtime model CRUD) | Add a governed registry service | Ops feedback |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Immutability & version integrity | 24 | 15.PF-FT-AI-SLM.md §155 | Runtime mutation possible? |
| EC-02 | Capability/purpose expressiveness | 20 | Feeds routing/fallback | Fields present |
| EC-03 | Governance & audit | 18 | Promotion control (ADR-D6-15) | Review/history |
| EC-04 | Simplicity / ops | 16 | Avoid a bespoke service | # systems |
| EC-05 | Query performance (resolve) | 12 | On hot path | Lookup latency |
| EC-06 | Extensibility (embeddings, rerankers) | 10 | One registry for all model types | Reuse |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Declarative config-as-code registry in Git, loaded into memory

**Description.** `config/models/*.yaml` (15.PF-FT-AI-SLM.md §15 shape) versioned in Git, promoted
via release manifest, loaded into an in-memory registry at startup.
**Strengths.** Immutable in prod; reviewable/auditable; fast in-memory resolve;
one mechanism for SLM + embedding + reranker; no extra service.
**Weaknesses.** Model status changes need a release (acceptable — governed change).
**Cost / effort.** Low.

### 5.2 Option B — Database-backed registry with admin API

**Description.** Models in a DB, edited via console.
**Strengths.** Runtime status flips (e.g. BLOCK a model fast).
**Weaknesses.** Runtime mutability vs §155; audit/rollback bespoke; new datastore.
**Cost / effort.** Higher; governance to re-impose.

### 5.3 Option C — Use the provider's own model catalogue as the registry

**Description.** Query HF/self-host for available models; no local registry.
**Strengths.** Nothing to maintain.
**Weaknesses.** No capability/purpose/status semantics; no allowlist; provider-shaped;
breaks on provider swap.
**Cost / effort.** Low, inadequate.

### 5.4 Option D — Registry inside the observability platform (Langfuse) or MLflow

**Description.** Track models/versions in an ML lifecycle tool.
**Strengths.** Rich lineage/experiment tracking.
**Weaknesses.** Runtime dependency on the critical resolve path; source-of-truth
moves out of Git; more than needed for a small model set. Better as a *mirror* for
experiment lineage.
**Cost / effort.** Medium; coupling.

### 5.5 Option E — Hybrid: Git-canonical config + emergency runtime BLOCK flag

**Description.** Option A plus a narrow, audited runtime kill-switch to set a model
BLOCKED without a full release (for incident response).
**Strengths.** Immutability for normal changes + fast incident containment.
**Weaknesses.** Two paths; the kill-switch must be tightly governed and logged.
**Cost / effort.** Low over A; small added control surface.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No registry (hard-coded model IDs) | DR-F-01/DR-C-02 — no routing/fallback/allowlist |
| Per-workflow model config duplication | Drift; no single source |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 15.PF-FT-AI-SLM.md §8–§12/§151–§155.

| Criterion | Weight | A: Git config | B: DB+API | C: Provider catalogue | D: Langfuse/MLflow | E: Git + kill-switch |
|---|---|---|---|---|---|---|
| EC-01 Immutability | 24 | 5 | 2 | 2 | 3 | 5 |
| EC-02 Expressiveness | 20 | 5 | 5 | 1 | 4 | 5 |
| EC-03 Governance/audit | 18 | 5 | 3 | 1 | 4 | 5 |
| EC-04 Simplicity/ops | 16 | 5 | 2 | 4 | 3 | 4 |
| EC-05 Resolve perf | 12 | 5 | 3 | 2 | 3 | 5 |
| EC-06 Extensibility | 10 | 5 | 4 | 1 | 4 | 5 |
| **Weighted total** | **100** | **500** | **314** | **178** | **358** | **488** |

Totals (×20): **A = 500**, **E = 488**, **D = 358**, **B = 314**, **C = 178**.

**Sensitivity.** A and E are within 12 points; the only differentiator is the
emergency BLOCK capability. Because a fast incident kill-switch has real operational
value and preserves immutability for all normal changes, **E is selected as A plus a
tightly-governed BLOCK flag**.

## 7. Decision

**PFF AI will implement a declarative, Git-canonical model registry
(config-as-code) loaded in-memory, extended with a narrowly-scoped, fully-audited
runtime BLOCK kill-switch for incident response (Option E).** The registry records
every SLM/embedding/reranker model by `id@version` with capabilities, purpose/task
class, status (15.PF-FT-AI-SLM.md §10) and compatibility (§153); routing (ADR-D3-16), fallback
(ADR-D3-18) and the provider allowlist (ADR-D3-14) read from it. Normal model
changes go through versioned promotion (ADR-D6-15); only an emergency BLOCK may be
applied at runtime, and it is logged and reconciled back into Git. Options B/C/D
rejected for mutability/semantics/coupling.

**Status rationale.** `Accepted` — registry is mandated by 15.PF-FT-AI-SLM.md §8; the
kill-switch is a governed refinement.

## 8. Architecture Detail

- **Schema** (15.PF-FT-AI-SLM.md §15, §11–§12; 14.PF-FT-AI-EMBEDDING-VECTOR.md §15): `model_id`, `provider`, `version`,
  `type` (slm/embedding/reranker), `capabilities` (streaming, tools, structured,
  max_tokens, dimension), `purpose`/task-class, `status`, `model_compatibility`.
- **Loader** `src/pf_ft_ai/slm/registry/`: validates on load; unknown/BLOCKED model
  resolution raises `ModelError`.
- **BLOCK switch**: an audited control (via config service / feature flag) that can
  only *demote* a model to BLOCKED; it can never introduce or promote a model;
  every use is logged (ADR-D6-17) and must be reconciled into Git within SLA.
- **Promotion** (15.PF-FT-AI-SLM.md §151–§152, §155): status transitions ACTIVE⇄TESTING⇄
  DEPRECATED→RETIRED via release; prod versions immutable.

## 9. Consequences

### 9.1 Positive
- Single source for all model metadata; routing/fallback/allowlist all derive from it.
- Immutable normal changes + fast incident containment.

### 9.2 Negative
- Kill-switch is a second path needing strict governance/audit.

### 9.3 Neutral
- Registry doubles as the embedding-model record (ADR-D3-23).

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Pure single-path simplicity | Emergency incident containment | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Registry is metadata; no business authority |
| Precedence chain | Not applicable — model metadata layer |
| Four-state separation | Registry is config, not runtime state |
| Versioned artefacts | This ADR enforces model version immutability |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Kill-switch misused to bypass promotion | Low | High | M | Switch can only BLOCK; audited; reconciled | Security Architect | Low |
| RSK-02 | Stale registry vs deployed models | Low | Med | M | Startup validation; smoke test (15.PF-FT-AI-SLM.md §82) | ML Eng | Low |
| RSK-03 | Capability mis-declared → bad routing | Med | Med | M | Contract tests per model | ML Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Unregistered model calls | 0 | > 0 | Registry logs | Continuous |
| QM-02 | Model version in every trace | 100% | < 100% | Langfuse | Continuous |
| QM-03 | Kill-switch uses reconciled to Git within SLA | 100% | < 100% | Audit | Per incident |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Central allowlist reduces surface; kill-switch is a controlled admin path |
| Data classification touched | Internal |
| Personal data / PII | None |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | None |
| Audit and evidential requirements | All promotions + BLOCKs audited (ADR-D6-17) |
| Standards touched | ISO/IEC 42001, 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 |
| Repository paths | `src/pf_ft_ai/slm/registry/`, `config/models/` |
| Configuration | Model YAML; release manifest pins |
| Contracts / schemas | Model registry Pydantic schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-14, ADR-D5-06, ADR-D6-15 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Only registered+ACTIVE models resolve | Unit test |
| AC-02 | Prod model version immutable (no edit path) | Route/config audit |
| AC-03 | Kill-switch can only demote to BLOCKED | Unit test + audit review |
| AC-04 | Capability flags drive routing/fallback | Integration test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Model usage by id@version; status changes |
| Alerting | Unregistered call; kill-switch activation |
| Runbook | `docs/runbooks/model-registry.md` |
| Failure mode and degradation | Registry load fail → refuse start (fail closed) |
| Rollback | Revert config version |
| Support model impact | ML platform + release management |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Registry loader + schema | S | negligible | Reuses Git/CI |
| Kill-switch control | S | negligible | Feature-flag/config service |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Model set grows large / frequent status changes | Ops | Consider governed registry service (Option B) with immutability controls |
| RT-02 | Kill-switch used frequently | QM-03 | Investigate root cause; improve pre-prod eval |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 |
| Specification sections | 15.PF-FT-AI-SLM.md §8–§12, §56, §58, §83, §151–§155; 14.PF-FT-AI-EMBEDDING-VECTOR.md §15–§16 |
| Requirement IDs | SLM-REG-* |
| Build phases | 6 |
| Code paths | `src/pf_ft_ai/slm/registry/`, `config/models/` |
| Configuration | model YAML, release manifest |
| Tests | registry unit + contract suites |
| Upstream ADRs | ADR-D3-14, ADR-D5-06 |
| Downstream ADRs | ADR-D3-16, ADR-D3-18, ADR-D3-23 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
