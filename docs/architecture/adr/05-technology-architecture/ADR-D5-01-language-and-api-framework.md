---
id: ADR-D5-01
title: Language and API framework — Python + FastAPI
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Backend Lead, AI Architecture Lead]
reviewers: [AI Architecture Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-02, ADR-D5-03, ADR-D2-06, ADR-D5-16]
source_docs:
  - "MD files/6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9, §27, §28, §29"
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §8"
build_phases: [1]
impacted_paths:
  - src/pf_ft_ai/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-01 — Language and API framework — Python + FastAPI

## 1. Summary

PFF AI will be built in **Python** with **FastAPI** as the HTTP API framework. Python
is the lingua franca of the AI/agent ecosystem (LangGraph, Hugging Face, embeddings,
evaluation tooling), and FastAPI provides async-first, Pydantic-native, OpenAPI-typed
endpoints that match the platform's boundary-typing and async-I/O conventions (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md
§9, §27–§29; CLAUDE.md). This is a confirmed choice; the ADR records the reasoning.

## 2. Context and Problem Statement

27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9 fixes the Python version and §27–§29 the FastAPI standard, endpoint flow and
API versioning; CLAUDE.md names Python + FastAPI as the confirmed stack. The AI
orchestration layer must integrate LangGraph (ADR-D2-06), the Hugging Face SLM/
embedding stack (ADR-D3-13/23) and Python-centric evaluation tooling. The language and
framework choice constrains hiring, libraries, async model and performance. Recording
it prevents drift and documents why alternatives were not chosen.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | First-class AI/agent ecosystem (LangGraph, HF) | CLAUDE.md; ADR-D2-06 |
| DR-F-02 | Async-first HTTP with typed boundaries | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §24, §27; CLAUDE.md |
| DR-F-03 | OpenAPI/contract generation | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §29 |
| DR-N-01 | Adequate performance for I/O-bound orchestration | 26.PF-FT-AI-PERFORMANCE-COST.md §13–§14 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Workload is I/O-bound (network calls), not CPU-bound | Offload CPU work (26.PF-FT-AI-PERFORMANCE-COST.md §23) | Perf profiling |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | AI/agent ecosystem fit | 30 | LangGraph/HF are Python | Library availability |
| EC-02 | Async + typed boundary support | 22 | Matches conventions | Async/Pydantic native |
| EC-03 | Developer productivity/hiring | 18 | Team velocity | Talent pool |
| EC-04 | Performance (I/O-bound) | 14 | Latency budget | p95 under load |
| EC-05 | Ecosystem maturity/ops | 16 | Libraries, tooling | Maturity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Python + FastAPI

**Description.** Python 3.11+ with FastAPI (Starlette/uvicorn), Pydantic v2, async I/O.
**Strengths.** Best AI ecosystem; async; Pydantic-native; OpenAPI; large talent pool.
**Weaknesses.** GIL/CPU-bound limits (mitigated: offload, 26.PF-FT-AI-PERFORMANCE-COST.md §23).
**Cost / effort.** Low; aligns with all AI ADRs.

### 5.2 Option B — Python + Django REST Framework

**Description.** Django/DRF.
**Strengths.** Batteries-included; mature.
**Weaknesses.** Sync-first ORM-centric; heavier for a stateless orchestration API;
less async-native than FastAPI.
**Cost / effort.** Medium; poorer async fit.

### 5.3 Option C — Node.js/TypeScript + NestJS/Express

**Description.** TS backend.
**Strengths.** Strong async; typed; good web ecosystem.
**Weaknesses.** AI/agent ecosystem weaker (LangGraph-py, HF are Python-first); would
split the stack or force reimplementation.
**Cost / effort.** High friction with AI tooling.

### 5.4 Option D — Go + a web framework

**Description.** Go services.
**Strengths.** Excellent concurrency/perf; simple deploys.
**Weaknesses.** Sparse AI/LLM libraries; would need Python sidecars anyway; slower AI
iteration.
**Cost / effort.** High for AI work.

### 5.5 Option E — Java/Kotlin + Spring Boot

**Description.** JVM backend.
**Strengths.** Enterprise-mature; strong typing; performance.
**Weaknesses.** AI ecosystem thin vs Python; heavier; slower AI iteration.
**Cost / effort.** High for AI work.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Python + Flask | Less async/typed/OpenAPI than FastAPI |
| Rust web stack | AI ecosystem immature for this workload |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9/§27–§29 and the AI
ecosystem requirements of ADR-D2-06/D3-13.

| Criterion | Weight | A: Python+FastAPI | B: Django | C: Node/TS | D: Go | E: Java/Spring |
|---|---|---|---|---|---|---|
| EC-01 AI ecosystem | 30 | 5 | 5 | 2 | 2 | 2 |
| EC-02 Async+typed | 22 | 5 | 3 | 5 | 5 | 4 |
| EC-03 Productivity/hiring | 18 | 5 | 4 | 4 | 3 | 4 |
| EC-04 Performance | 14 | 4 | 3 | 4 | 5 | 5 |
| EC-05 Maturity/ops | 16 | 5 | 5 | 4 | 4 | 5 |
| **Weighted total** | **100** | **488** | **414** | **362** | **352** | **372** |

Totals (×20): **A = 488**, **B = 414**, **E = 372**, **C = 362**, **D = 352**.

**Sensitivity.** A leads B by 74. B (Django) only rivals on AI ecosystem (both Python)
but loses on async/typed fit — the deciding factor. Non-Python options lose decisively
on EC-01, which no realistic re-weighting overturns given the Python-first AI stack.

## 7. Decision

**PFF AI will be implemented in Python with FastAPI.** Python is mandated by the AI
ecosystem (LangGraph, Hugging Face); FastAPI provides the async-first, Pydantic-native,
OpenAPI-typed API layer that matches the platform's conventions. Django (B) is a weaker
async fit; non-Python options (C/D/E) fracture the AI stack.

**Status rationale.** `Accepted` — confirmed in CLAUDE.md and 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md.

## 8. Architecture Detail

- FastAPI app in `src/pf_ft_ai/api/`; async endpoints (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §27–§28) returning the
  standard envelope (ADR-D4-09); versioned paths `/api/v1/...` (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §29).
- Uvicorn/gunicorn workers on the container runtime (25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §8); dependency injection
  (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §32); shared async HTTP client (ADR-D5-16).
- CPU-bound work offloaded to avoid blocking the event loop (26.PF-FT-AI-PERFORMANCE-COST.md §23; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §25).

## 9. Consequences

### 9.1 Positive
- Seamless AI-library integration; async, typed, self-documenting API.
### 9.2 Negative
- GIL constrains CPU-bound throughput — mitigated by offloading and horizontal scale.
### 9.3 Neutral
- Sets language for all other ADRs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Raw CPU throughput of Go/JVM | AI ecosystem + async + productivity | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Language/framework choice; no business authority |
| Precedence chain | Not applicable |
| Four-state separation | Framework supports typed state boundaries |
| Versioned artefacts | API versioning in path |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | CPU-bound work blocks event loop | Med | Med | M | Offload (26.PF-FT-AI-PERFORMANCE-COST.md §23); profile | Backend Lead | Low |
| RSK-02 | Dependency sprawl in Python | Med | Low | L | Pinning/lock (ADR-D5-04) | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | API p95 latency (framework overhead) | low | breach | App Insights | Continuous |
| QM-02 | Blocking-call incidents | 0 | > 0 | Lint/async checks | Per build |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Standard web framework; hardened per 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §17–§18 |
| Data classification touched | Internal |
| Personal data / PII | Handled at app layer per ADR-D6-06 |
| Children's data and safeguarding | N/A at framework layer |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Request logging (ADR-D7-04) |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `src/pf_ft_ai/` |
| Configuration | uvicorn/gunicorn settings |
| Contracts / schemas | FastAPI + Pydantic models |
| Migration | N/A (greenfield) |
| Dependencies on other ADRs | ADR-D5-02, D5-03, D2-06 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | API endpoints are async and typed | Code review |
| AC-02 | Versioned paths used | Route audit |
| AC-03 | No blocking calls in async paths | Lint check |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Request metrics, latency |
| Alerting | Latency/error spikes |
| Runbook | `docs/runbooks/api.md` |
| Failure mode and degradation | Standard HTTP error envelope (ADR-D4-09) |
| Rollback | Deploy previous image |
| Support model impact | Backend team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Framework | none | none | Open-source |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Sustained CPU-bound bottleneck | Perf metrics | Offload service (Go/Rust) behind the API |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 Technology |
| Specification sections | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9, §27–§29; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §8 |
| Requirement IDs | TECH-LANG-* |
| Build phases | 1 |
| Code paths | `src/pf_ft_ai/` |
| Configuration | server config |
| Tests | API smoke suite |
| Upstream ADRs | — |
| Downstream ADRs | ADR-D5-02, D5-03, D2-06 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
