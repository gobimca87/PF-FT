---
id: ADR-D7-03
title: Correlation ID and trace-propagation standard
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Backend Lead, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-01, ADR-D7-02, ADR-D4-09, ADR-D2-16, ADR-D6-17]
source_docs:
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §7, §8, §9, §10, §41"
  - "MD files/3 Context & Integration/10 PF-FT-AI-ENTERPRISE-INTEGRATION.md §84"
build_phases: [2]
impacted_paths:
  - src/pf_ft_ai/observability/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-03 — Correlation ID and trace-propagation standard

## 1. Summary

Every request carries a **correlation ID** propagated via **W3C Trace Context** across
API, orchestration, tools, enterprise calls and Service Bus events, so one conversation/
workflow is traceable end-to-end across platform logs, Langfuse traces and the audit
record (doc 24 §7–§10, §41; doc 10 §84). The correlation ID appears in the response
envelope (ADR-D4-09) and every telemetry/audit record.

## 2. Context and Problem Statement

Doc 24 §7–§9 define the correlation model/flow/requirements, §10 trace-context
propagation, §41 event correlation; doc 10 §84 the correlation id. Without a single
propagated id, telemetry across hops (sync + async events) can't be stitched into one
story, crippling incident response. This ADR fixes the correlation-id and propagation
standard.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | One correlation id per request/workflow | doc 24 §7–§9 |
| DR-F-02 | Propagate across sync + async (events) | doc 24 §10, §41; ADR-D2-16 |
| DR-F-03 | Present in logs/traces/audit/envelope | doc 24 §9; ADR-D4-09, D6-17 |
| DR-N-01 | Standard format (W3C Trace Context) | doc 24 §10 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise APIs accept/return a correlation header | Map to their scheme | Integration review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | End-to-end traceability | 30 | Incident response | Stitchability |
| EC-02 | Sync + async coverage | 24 | Events too | Event correlation |
| EC-03 | Standard/interop | 18 | W3C; enterprise | Format |
| EC-04 | Simplicity/consistency | 16 | One scheme | Consistency |
| EC-05 | Overhead | 12 | Header cost | Negligible |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — W3C Trace Context correlation id, propagated sync + via event envelope

**Description.** Generate/accept a `traceparent`/correlation id at the edge (APIM/API);
propagate through orchestration, tools, enterprise calls, and into the Service Bus event
envelope (ADR-D2-17); include in logs/traces/audit/response.
**Strengths.** Standard, full coverage, interoperable.
**Weaknesses.** Must thread through async boundaries.
**Cost / effort.** Low.

### 5.2 Option B — Custom correlation header (non-W3C)

**Description.** A bespoke id header.
**Strengths.** Simple.
**Weaknesses.** No OTel/W3C interop; reinvents a standard.
**Cost / effort.** Low; non-standard.

### 5.3 Option C — Per-service ids, joined later by logs

**Description.** Each service logs its own id; correlate offline.
**Strengths.** No propagation.
**Weaknesses.** Fragile joins; async gaps; poor real-time tracing.
**Cost / effort.** Low; weak.

### 5.4 Option D — Sync-only propagation (no event correlation)

**Description.** Propagate on HTTP only.
**Strengths.** Simpler.
**Weaknesses.** Async event flows (ERC refresh, workflows) untraceable end-to-end.
**Cost / effort.** Low; gaps.

### 5.5 Option E — W3C Trace Context + business correlation keys (conversation/workflow id)

**Description.** Option A plus stable business keys (conversation id, workflow instance
id) alongside the trace id for cross-session correlation.
**Strengths.** Trace-level + business-level correlation.
**Weaknesses.** Slightly more fields.
**Cost / effort.** Low.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No correlation id | doc 24 §7 |
| Correlation only in Langfuse | Needs to span logs/audit too |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 24 §7–§10/§41 and doc 10 §84.

| Criterion | Weight | A: W3C sync+async | B: Custom header | C: Per-service | D: Sync-only | E: W3C+business keys |
|---|---|---|---|---|---|---|
| EC-01 Traceability | 30 | 5 | 4 | 2 | 3 | 5 |
| EC-02 Sync+async | 24 | 5 | 4 | 2 | 1 | 5 |
| EC-03 Standard | 18 | 5 | 2 | 3 | 4 | 5 |
| EC-04 Simplicity | 16 | 4 | 5 | 3 | 4 | 4 |
| EC-05 Overhead | 12 | 5 | 5 | 4 | 5 | 4 |
| **Weighted total** | **100** | **484** | **388** | **262** | **306** | **488** |

Totals (×20): **E = 488**, **A = 484**, **B = 388**, **D = 306**, **C = 262**.

**Sensitivity.** E (W3C + business keys) edges A by adding conversation/workflow-level
correlation useful across sessions/events. Adopted. Custom (B), per-service (C) and
sync-only (D) all lose on standardisation/coverage.

## 7. Decision

**PFF AI will use W3C Trace Context for correlation, propagated across sync calls and via
the Service Bus event envelope, augmented with stable business correlation keys
(conversation id, workflow instance id), and included in every log, Langfuse trace,
audit record and response envelope (Option E).** Custom headers (B), per-service ids (C)
and sync-only propagation (D) are rejected.

## 8. Architecture Detail

- Edge (APIM/API) generates/accepts `traceparent`; middleware injects it into context;
  the shared HTTP client (ADR-D5-16) forwards it; the event envelope (ADR-D2-17) carries
  it for async flows (§41).
- Business keys (conversation/workflow id) travel alongside; all telemetry (ADR-D7-01/02)
  and audit (ADR-D6-17) records include both; response envelope (ADR-D4-09) returns the
  correlation id.

## 9. Consequences

### 9.1 Positive
- One conversation/workflow traceable end-to-end across sync + async and all sinks.
### 9.2 Negative
- Threading through async boundaries.
### 9.3 Neutral
- Underpins observability + audit.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| A couple of extra fields | End-to-end + business correlation | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Correlation aids tracing; no business authority |
| Precedence chain | N/A |
| Four-state separation | Correlation ids are metadata, not state |
| Versioned artefacts | Correlation scheme documented |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Correlation dropped across async | Med | Med | M | Envelope carries id; tests | Backend Lead | Low |
| RSK-02 | Enterprise API lacks header | Low | Low | L | Map to their scheme | Integration Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Records with correlation id | 100% | < 100% | Telemetry audit | Continuous |
| QM-02 | Async flows correlated | 100% | < 100% | Event traces | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Correlation ids (non-PII) |
| Personal data / PII | Ids are opaque, not PII |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Ties audit to requests |
| Standards touched | W3C Trace Context; ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `src/pf_ft_ai/observability/`, middleware |
| Configuration | Header names; propagation |
| Contracts / schemas | Envelope + event fields |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-16, D2-16/17, D4-09 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Correlation id on every record | Telemetry audit |
| AC-02 | Propagates across events | Event trace test |
| AC-03 | Returned in response envelope | API test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Correlation coverage |
| Alerting | Missing correlation |
| Runbook | `docs/runbooks/observability.md` |
| Failure mode and degradation | Missing id generated at edge |
| Rollback | Config revert |
| Support model impact | SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Middleware/propagation | S | none | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Correlation gaps in incidents | Post-incident | Fix propagation gap |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | doc 24 §7–§10, §41; doc 10 §84 |
| Requirement IDs | OBS-CORR-* |
| Build phases | 2 |
| Code paths | middleware/observability |
| Configuration | propagation |
| Tests | correlation suites |
| Upstream ADRs | ADR-D5-16, D2-16 |
| Downstream ADRs | ADR-D7-01, D7-02, D6-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
