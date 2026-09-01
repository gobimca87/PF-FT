---
id: ADR-D5-03
title: Boundary validation standard — Pydantic v2
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [AI Architecture Lead, Principal Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-02, ADR-D2-07, ADR-D4-09, ADR-D3-17]
source_docs:
  - "MD files/6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16, §17, §36"
build_phases: [1]
impacted_paths:
  - src/pf_ft_ai/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-03 — Boundary validation standard — Pydantic v2

## 1. Summary

PFF AI will use **Pydantic v2** for all data crossing a boundary — FastAPI
request/response, tool req/res, config, event contracts, ERC schema, SLM req/res —
while **LangGraph-internal state uses `TypedDict`** (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16–§17, §36; CLAUDE.md).
Pydantic v2's Rust-core performance and strict validation make it the single boundary
validation standard.

## 2. Context and Problem Statement

CLAUDE.md fixes Pydantic for boundaries and TypedDict for LangGraph state; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16
sets the Pydantic standard and §17 the validation standard, §36 the typed graph state.
Without one validation standard, boundaries validate inconsistently (some ad hoc, some
dataclasses), weakening the type guarantees mypy (ADR-D5-02) provides and the envelope
contract (ADR-D4-09). This ADR fixes the boundary-validation library and the
Pydantic/TypedDict split.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Validate all boundary data | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16–§17; CLAUDE.md |
| DR-F-02 | TypedDict for LangGraph internal state | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §36; CLAUDE.md |
| DR-N-01 | High-performance validation | 26.PF-FT-AI-PERFORMANCE-COST.md §14 |
| DR-N-02 | mypy plugin support | ADR-D5-02 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Pydantic v2 perf adequate on hot paths | Optimise/model_validate tuning | Perf tests |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Validation strength/ergonomics | 28 | Correctness at boundary | Feature fit |
| EC-02 | Performance | 22 | Hot paths | Validate latency |
| EC-03 | FastAPI + mypy integration | 20 | Ecosystem | Native support |
| EC-04 | Serialization (JSON/schema) | 16 | Envelope/OpenAPI | Round-trip |
| EC-05 | Maturity/adoption | 14 | Stability | Adoption |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Pydantic v2 at boundaries + TypedDict for graph state

**Description.** Pydantic v2 models at every boundary; TypedDict for LangGraph state.
**Strengths.** Fast (Rust core); FastAPI-native; mypy plugin; JSON-schema/OpenAPI;
matches CLAUDE.md exactly.
**Weaknesses.** Two representations (Pydantic vs TypedDict) — but that split is
intentional.
**Cost / effort.** Low.

### 5.2 Option B — Dataclasses + manual validation

**Description.** stdlib dataclasses with hand-written validators.
**Strengths.** No dependency.
**Weaknesses.** Manual, error-prone validation; no JSON-schema; weaker FastAPI fit.
**Cost / effort.** High maintenance.

### 5.3 Option C — attrs + cattrs

**Description.** attrs models with cattrs (de)serialization.
**Strengths.** Fast; flexible.
**Weaknesses.** Less FastAPI-native; smaller ecosystem for API/OpenAPI; more wiring.
**Cost / effort.** Medium.

### 5.4 Option D — Pydantic v1

**Description.** Stay on v1.
**Strengths.** Familiar.
**Weaknesses.** Slower (pure Python); v1 EOL trajectory; misses v2 features.
**Cost / effort.** Low now, debt later.

### 5.5 Option E — marshmallow

**Description.** marshmallow schemas.
**Strengths.** Mature serialization.
**Weaknesses.** Separate from type hints; not FastAPI-native; extra mapping.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No boundary validation | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §17 |
| Pydantic everywhere incl. graph state | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §36 — TypedDict for LangGraph |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16–§17/§36 and CLAUDE.md.

| Criterion | Weight | A: Pydantic v2 | B: dataclasses | C: attrs+cattrs | D: Pydantic v1 | E: marshmallow |
|---|---|---|---|---|---|---|
| EC-01 Validation | 28 | 5 | 2 | 4 | 4 | 4 |
| EC-02 Performance | 22 | 5 | 4 | 5 | 2 | 3 |
| EC-03 FastAPI+mypy | 20 | 5 | 3 | 3 | 4 | 2 |
| EC-04 Serialization | 16 | 5 | 2 | 4 | 4 | 5 |
| EC-05 Maturity | 14 | 5 | 5 | 4 | 4 | 4 |
| **Weighted total** | **100** | **500** | **312** | **408** | **352** | **352** |

Totals (×20): **A = 500**, **C = 408**, **D = 352**, **E = 352**, **B = 312**.

**Sensitivity.** A is a clean sweep. C (attrs) is the nearest but loses on FastAPI/mypy
nativeness — the deciding ecosystem factor. No re-weighting changes the outcome.

## 7. Decision

**PFF AI will use Pydantic v2 for all boundary data and TypedDict for LangGraph
internal state (Option A).** This is CLAUDE.md's rule; Pydantic v2's performance,
FastAPI/mypy integration and JSON-schema output make it the standard. Dataclasses (B),
attrs (C), Pydantic v1 (D) and marshmallow (E) are rejected.

**Status rationale.** `Accepted` — confirmed in CLAUDE.md and 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md.

## 8. Architecture Detail

- Boundary models subclass `pydantic.BaseModel` (v2); `model_validate`/`model_dump`
  at edges; strict types; `pydantic.mypy` plugin (ADR-D5-02).
- LangGraph state as `TypedDict` (ADR-D2-07); conversion Pydantic↔TypedDict at the
  orchestration boundary.
- Envelope + error models (ADR-D4-09) and SLM/tool/ERC/event contracts are Pydantic.

## 9. Consequences

### 9.1 Positive
- Uniform, fast, typed validation; OpenAPI/JSON-schema for free.
### 9.2 Negative
- Two state representations (intentional split) require conversion.
### 9.3 Neutral
- Underlies most other contracts.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single representation everywhere | Right tool per layer (Pydantic/TypedDict) | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Validation library; no business authority |
| Precedence chain | Validates data faithfully at boundaries |
| Four-state separation | Pydantic boundaries + TypedDict state (ADR-D2-07) |
| Versioned artefacts | Schemas versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Validation overhead on hot path | Low | Low | L | Profile; reuse models | Backend Lead | Low |
| RSK-02 | Pydantic↔TypedDict drift | Med | Med | M | Single conversion layer + tests | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Boundaries with Pydantic validation | 100% | < 100% | Code review | Per release |
| QM-02 | Graph state uses TypedDict | 100% | < 100% | Review | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Input validation reduces injection/malformed data risk |
| Data classification touched | Internal |
| Personal data / PII | Schema constrains fields |
| Children's data and safeguarding | N/A at library layer |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Schemas documented |
| Standards touched | ISO/IEC 27001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `src/pf_ft_ai/` |
| Configuration | pydantic settings |
| Contracts / schemas | All boundary models |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-02, D2-07, D4-09 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All boundaries use Pydantic v2 | Code review |
| AC-02 | LangGraph state uses TypedDict | Review |
| AC-03 | mypy plugin catches model errors | CI |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Validation error rates |
| Alerting | Validation failure spikes |
| Runbook | `docs/runbooks/api.md` |
| Failure mode and degradation | Invalid input → 4xx envelope (ADR-D4-09) |
| Rollback | Schema version revert |
| Support model impact | Backend team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Library | none | none | Open-source |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Validation a measured bottleneck | Perf | Optimise models/paths |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 |
| Specification sections | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16–§17, §36 |
| Requirement IDs | TECH-VAL-* |
| Build phases | 1 |
| Code paths | `src/pf_ft_ai/` |
| Configuration | pydantic |
| Tests | validation suites |
| Upstream ADRs | ADR-D5-02 |
| Downstream ADRs | ADR-D2-07, D4-09, D3-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
