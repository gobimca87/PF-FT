---
id: ADR-D3-19
title: Streaming strategy and its interaction with structured output
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Frontend Engineer, Conversation Designer]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-17, ADR-D3-14, ADR-D2-04, ADR-D6-09, ADR-D2-19]
source_docs:
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §47, §48"
  - "MD files/4 AI/16.PF-FT-AI-PROMPT-ENGINEERING.md §141"
build_phases: [6, 7]
impacted_paths:
  - src/pf_ft_ai/api/
  - src/pf_ft_ai/slm/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-19 — Streaming strategy and its interaction with structured output

## 1. Summary

PFF AI will **stream user-facing persona narration** token-by-token for
responsiveness, but will **never stream structured output, tool arguments, or any
text that must pass validation or guardrails before the user sees it**. Streaming is
a presentation optimisation on already-decided, guardrail-cleared content; it must
never let unvalidated or unconfirmed text reach the user (doc 15 §47–§48). Where a
turn contains both a decision/tool step and narration, the decision completes and is
validated first; only the final narration streams.

## 2. Context and Problem Statement

Doc 15 §47 introduces streaming and §48 warns explicitly about streaming and
structured output; doc 16 §141 covers citation handling in output. Streaming
improves perceived latency but conflicts with three hard requirements: structured
output must be validated whole before use (ADR-D3-17); guardrails must vet output
before the user sees it (ADR-D6-09); and Adam must never state an unconfirmed
transaction outcome (CLAUDE.md §Adam 6). Without a decision, a naive
"stream-everything" implementation would surface unvalidated JSON, partial tool
intentions, or a premature "GOAL!" before enterprise confirmation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Stream persona narration for responsiveness | doc 15 §47 |
| DR-F-02 | Never stream unvalidated structured output | doc 15 §48; ADR-D3-17 |
| DR-C-01 | Guardrails vet output before user sees it | ADR-D6-09 |
| DR-C-02 | No unconfirmed transaction stated | CLAUDE.md §Adam 6 |
| DR-N-01 | Perceived latency improvement | UX target |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Output guardrails can operate on the final text pre-stream or on safe increments | Buffer fully before streaming | Guardrail design (ADR-D6-09) |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Safety (no unvalidated/unconfirmed text streamed) | 32 | Non-negotiable | Leak tests |
| EC-02 | Perceived latency / UX | 22 | Why stream at all | Time-to-first-token |
| EC-03 | Guardrail compatibility | 18 | Must vet output | Guardrail coverage |
| EC-04 | Implementation complexity | 14 | Maintainability | Concepts |
| EC-05 | Provider portability | 8 | HF/self-host differ | Parity |
| EC-06 | Cost | 6 | Streaming overhead | Minor |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Stream final narration only; buffer+validate everything else

**Description.** Decision/tool/structured steps run fully and are validated and
guardrail-cleared; only the final persona narration streams to the user.
**Strengths.** Safe by construction; good perceived latency for the visible message;
guardrails run on the decided content.
**Weaknesses.** No streaming during the "thinking"/tool phase (fill with status).
**Cost / effort.** Low-medium.

### 5.2 Option B — Stream everything token-by-token

**Description.** Stream all model output including structured/tool content.
**Strengths.** Lowest time-to-first-token.
**Weaknesses.** Surfaces unvalidated JSON/partial tool intent; can state unconfirmed
outcomes; guardrails can't vet whole output first. Violates DR-F-02/DR-C-01/DR-C-02.
**Cost / effort.** Low, unsafe.

### 5.3 Option C — No streaming (buffer all, send complete)

**Description.** Always return the complete message.
**Strengths.** Simplest; fully guardrail-vetted.
**Weaknesses.** Worse perceived latency on long narration.
**Cost / effort.** Low; weaker UX.

### 5.4 Option D — Chunk-level streaming with per-chunk guardrail vetting

**Description.** Stream sentence/paragraph chunks, each guardrail-checked before
emission.
**Strengths.** Streams safely with incremental delivery.
**Weaknesses.** More complex; some guardrails need whole-message context; risk of
retracting an already-shown chunk.
**Cost / effort.** Medium-high.

### 5.5 Option E — Optimistic stream with cancel/redact on guardrail trip

**Description.** Stream immediately; retract/redact if a guardrail later trips.
**Strengths.** Fastest visible start.
**Weaknesses.** Users may see content that is then retracted — unacceptable for
enterprise/safeguarding correctness; can't un-show a premature "GOAL!".
**Cost / effort.** Medium; unsafe UX.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Stream tool-call arguments to user | DR-F-02; meaningless + unsafe |
| Stream before enterprise confirmation on transactions | DR-C-02 (CLAUDE.md §Adam 6) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 15 §47–§48 and the guardrail
placement of ADR-D6-09.

| Criterion | Weight | A: Narration-only | B: Everything | C: No stream | D: Chunk+vet | E: Optimistic+redact |
|---|---|---|---|---|---|---|
| EC-01 Safety | 32 | 5 | 1 | 5 | 4 | 2 |
| EC-02 UX/latency | 22 | 4 | 5 | 2 | 5 | 5 |
| EC-03 Guardrail compat | 18 | 5 | 1 | 5 | 4 | 2 |
| EC-04 Complexity | 14 | 4 | 5 | 5 | 2 | 3 |
| EC-05 Portability | 8 | 4 | 4 | 5 | 3 | 3 |
| EC-06 Cost | 6 | 5 | 4 | 5 | 3 | 3 |
| **Weighted total** | **100** | **458** | **278** | **436** | **388** | **288** |

Totals (×20): **A = 458**, **C = 436**, **D = 388**, **E = 288**, **B = 278**.

**Sensitivity.** A leads C by 22 (the UX gain of streaming narration) and both
dominate on safety. D (chunk-level) is a viable future enhancement if whole-message
guardrails can be made incremental (RT-01), but its retraction risk keeps it behind
A now. B and E are unsafe.

## 7. Decision

**PFF AI will stream only the final, guardrail-cleared persona narration
(Option A).** All decision, routing, tool-argument and structured-output steps run to
completion and are validated (ADR-D3-17) and guardrail-vetted (ADR-D6-09) before any
user-visible text is emitted; transaction outcomes are stated only after enterprise
confirmation (CLAUDE.md §Adam 6). During non-streamed phases the Conversation
Manager (ADR-D2-04) may show workflow status ("VAR check in progress"). Chunk-level
vetted streaming (D) is a documented future option; B and E are rejected as unsafe.

**Status rationale.** `Accepted` — doc 15 §48's warning and the guardrail/persona
rules make this the only safe posture; ADR records the rationale.

## 8. Architecture Detail

- The SLM abstraction (ADR-D3-14) exposes `stream()` used **only** for narration
  tasks (task class from ADR-D3-16); structured/tool calls use non-streaming
  `generate`/`generate_structured`.
- Output guardrails (ADR-D6-09) run on the final narration before/at stream start;
  if a guardrail can only judge whole text, the message is buffered then streamed as
  a fast replay (still improves nothing over C for that case — used sparingly).
- Portal links are resolved and stripped/validated (ADR-D2-19) before streaming, so
  no invented URL can be streamed.
- The API (FastAPI, ADR-D2-04) uses SSE/chunked transfer for the narration stream;
  the turn's decision/tool results are already committed to workflow state.

## 9. Consequences

### 9.1 Positive
- Responsive UX without ever exposing unvalidated/unconfirmed content.
### 9.2 Negative
- No token streaming during tool/thinking phases (status messages fill the gap).
### 9.3 Neutral
- Streaming is cleanly separated from decision logic.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Fastest-possible first token (B/E) | Safety, guardrail vetting, honesty | AI Arch Lead, Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | No decision/outcome streamed before it is made/confirmed |
| Precedence chain | Streaming is presentation of already-decided content |
| Four-state separation | Decision committed to workflow state before narration streams |
| Versioned artefacts | Streaming policy is config/versioned |
| Adam persona governs *how*, not *what* | Streaming affects delivery of wording only; never states unconfirmed truth |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Unvalidated content streamed via misconfig | Low | High | M | Streaming allowed only for narration class; tests | ML Eng | Low |
| RSK-02 | Premature outcome streamed | Low | High | M | Confirmation gate before narration (ADR-D3-08) | Security Architect | Low |
| RSK-03 | Guardrail can't vet incrementally | Med | Med | M | Buffer-then-send for whole-message guardrails | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Unvalidated/unconfirmed text streamed | 0 | > 0 | Security tests | Continuous |
| QM-02 | Time-to-first-visible-token (narration) | ≤ 1s | > 3s | App Insights | Continuous |
| QM-03 | Guardrail coverage on streamed output | 100% | < 100% | Tests | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Streaming path constrained to vetted narration only |
| Data classification touched | Internal |
| Personal data / PII | Guardrails/redaction run before stream |
| Children's data and safeguarding | No unvetted safeguarding content can stream |
| UK GDPR lawful basis and rights impact | None |
| Audit and evidential requirements | Final message logged as delivered |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (SLM), 7 (API/conversation) |
| Repository paths | `src/pf_ft_ai/api/`, `src/pf_ft_ai/slm/` |
| Configuration | Streaming enabled per task class (narration only) |
| Contracts / schemas | SSE/stream event contract |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-17, ADR-D6-09, ADR-D2-04, ADR-D2-19 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Only narration class can stream | Config + unit test |
| AC-02 | Structured/tool output never streamed | Code path audit |
| AC-03 | Guardrails run before user sees streamed text | Integration test (ADR-D6-09) |
| AC-04 | No outcome streamed before confirmation | Test (ADR-D3-08) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Time-to-first-token; stream errors |
| Alerting | Stream failures; any unvetted-stream detection |
| Runbook | `docs/runbooks/conversation.md` |
| Failure mode and degradation | Stream failure → fall back to complete-message send |
| Rollback | Disable streaming via config (revert to Option C) |
| Support model impact | Frontend + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Streaming API + wiring | M | negligible | Build |
| Streaming overhead | — | minimal | Connection handling |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Incremental guardrails become feasible | ADR-D6-09 evolution | Evaluate chunk-level streaming (Option D) |
| RT-02 | Any unvetted-stream incident | Incident | CAR; tighten policy |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 |
| Specification sections | doc 15 §47–§48; doc 16 §141 |
| Requirement IDs | SLM-STREAM-* |
| Build phases | 6, 7 |
| Code paths | `src/pf_ft_ai/api/`, `src/pf_ft_ai/slm/` |
| Configuration | streaming task-class flag |
| Tests | stream safety + guardrail suites |
| Upstream ADRs | ADR-D3-17, ADR-D6-09 |
| Downstream ADRs | ADR-D2-04 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
