---
id: ADR-D7-05
title: Error taxonomy and the PlatformError hierarchy
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [AI Architecture Lead, SRE]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-09, ADR-D7-06, ADR-D3-18, ADR-D2-11, ADR-D7-04]
source_docs:
  - "MD files/6 Production/24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §51, §52, §53, §54"
build_phases: [1]
impacted_paths:
  - src/pff_fa_ai/common/errors.py
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-05 — Error taxonomy and the PlatformError hierarchy

## 1. Summary

PFF AI will use a single **`PlatformError` exception hierarchy** — `ValidationError`,
`ConfigurationError`, `IntegrationError`, `ToolError`, `ModelError`, `RAGError`,
`GuardrailError`, `WorkflowError` (CLAUDE.md) — each carrying **structured fields
(code, severity, retryable)** that drive error translation (ADR-D4-09), retry
classification (ADR-D3-18/D2-11) and severity-based alerting (24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §51–§54). Errors
are classified, not stringly-typed.

## 2. Context and Problem Statement

24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §51 error taxonomy, §52 error structure, §53 error severity, §54 retry
classification; CLAUDE.md fixes the `PlatformError` root and its subclasses. Without a
consistent taxonomy, error handling is ad hoc: retries fire on non-retryable errors,
severities are guessed, and the response envelope (ADR-D4-09) can't map codes reliably.
This ADR fixes the exception hierarchy and its structured semantics.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Single PlatformError hierarchy | CLAUDE.md |
| DR-F-02 | Structured fields: code, severity, retryable | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §52–§54 |
| DR-F-03 | Drive translation/retry/alerting from taxonomy | ADR-D4-09, D3-18, D7-08 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Subclasses cover the error space | Add subclasses | Error review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Consistent classification | 28 | Reliable handling | Coverage |
| EC-02 | Drives retry correctly | 22 | No bad retries | Retry accuracy |
| EC-03 | Drives severity/alerting | 18 | Right alerts | Severity mapping |
| EC-04 | Envelope/code mapping | 16 | Client contract | Mapping (ADR-D4-09) |
| EC-05 | Simplicity/maintainability | 16 | Usable | Hierarchy clarity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — PlatformError hierarchy with structured fields (code/severity/retryable)

**Description.** Root `PlatformError`; the eight CLAUDE.md subclasses; each instance
carries `code`, `severity`, `retryable`, `details`; handlers use these for translation
(ADR-D4-09), retry (ADR-D3-18/D2-11) and alerting (ADR-D7-08).
**Strengths.** Consistent, drives all handling, maps to codes.
**Weaknesses.** Discipline to raise the right type.
**Cost / effort.** Low.

### 5.2 Option B — Generic exceptions + string messages

**Description.** Use built-in exceptions with messages.
**Strengths.** Simplest.
**Weaknesses.** No structured handling; string-matching; unreliable retry/severity.
**Cost / effort.** Low; fragile.

### 5.3 Option C — Error codes only (no exception hierarchy)

**Description.** Return codes, no typed exceptions.
**Strengths.** Explicit codes.
**Weaknesses.** Loses Python exception ergonomics; error handling verbose.
**Cost / effort.** Medium.

### 5.4 Option D — Result/Either type (no exceptions)

**Description.** Functional error returns.
**Strengths.** Explicit control flow.
**Weaknesses.** Against Python idiom + FastAPI; large refactor; mixed with libs that
raise.
**Cost / effort.** High.

### 5.5 Option E — PlatformError hierarchy + error catalogue (registry of codes/severities)

**Description.** Option A plus a central catalogue mapping each error code to severity,
retryability, user message and alert routing.
**Strengths.** Single source of truth for error semantics; consistent envelope + alerts.
**Weaknesses.** Catalogue upkeep.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Ad-hoc per-module exceptions | CLAUDE.md single hierarchy |
| Retry on all errors | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §54, §58 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §51–§54 and CLAUDE.md.

| Criterion | Weight | A: Hierarchy+fields | B: Generic+strings | C: Codes-only | D: Result type | E: Hierarchy+catalogue |
|---|---|---|---|---|---|---|
| EC-01 Classification | 28 | 5 | 2 | 4 | 4 | 5 |
| EC-02 Retry correctness | 22 | 5 | 2 | 4 | 4 | 5 |
| EC-03 Severity/alerting | 18 | 5 | 2 | 4 | 3 | 5 |
| EC-04 Envelope mapping | 16 | 5 | 2 | 5 | 3 | 5 |
| EC-05 Simplicity | 16 | 4 | 5 | 3 | 2 | 4 |
| **Weighted total** | **100** | **484** | **252** | **396** | **340** | **492** |

Totals (×20): **E = 492**, **A = 484**, **C = 396**, **D = 340**, **B = 252**.

**Sensitivity.** E (hierarchy + central error catalogue) edges A by giving one source of
truth for code→severity/retry/message/alert. Adopted. Generic-strings (B) is fragile;
Result-type (D) fights the Python/FastAPI idiom.

## 7. Decision

**PFF AI will use the `PlatformError` hierarchy (eight CLAUDE.md subclasses) with
structured fields (code, severity, retryable, details) plus a central error catalogue
mapping each code to severity, retryability, safe user message and alert routing
(Option E).** The taxonomy drives error translation (ADR-D4-09), retry classification
(ADR-D3-18/D2-11) and alerting (ADR-D7-08). Generic exceptions (B), codes-only (C) and
Result-type (D) are rejected.

## 8. Architecture Detail

- `src/pff_fa_ai/common/errors.py`: `PlatformError(code, severity, retryable, details)`
  and subclasses; a catalogue (config) maps codes → severity/retry/user-message/alert.
- Retry classification (24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §54–§58): only `retryable=True` errors retried (ADR-D3-18/
  D2-11); the retry anti-pattern (§58) avoided.
- Envelope mapping (ADR-D4-09) translates subclass→`PFF.<CATEGORY>.<NAME>`; severity
  drives alert routing (ADR-D7-08); logs/audit record the code (ADR-D7-04/D6-17).

## 9. Consequences

### 9.1 Positive
- Consistent, structured error handling driving retry/severity/translation from one place.
### 9.2 Negative
- Catalogue + discipline to raise correct types.
### 9.3 Neutral
- Underpins resilience (D7-06) and envelope (D4-09).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Ad-hoc exception freedom | Consistent, driven handling | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Errors surfaced faithfully, not hidden |
| Precedence chain | N/A |
| Four-state separation | Errors carry no unredacted state |
| Versioned artefacts | Error catalogue versioned |
| Adam persona governs *how*, not *what* | Persona communicates errors factually (CLAUDE.md §Adam 7) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Wrong error type → wrong retry | Med | Med | M | Catalogue + tests; retryable field | Backend Lead | Low |
| RSK-02 | Unmapped error → generic INTERNAL | Low | Low | L | Catch-all mapping (ADR-D4-09) | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Errors as PlatformError subclasses | ≥ target | falling | Code audit | Per release |
| QM-02 | Retries on non-retryable errors | 0 | > 0 | Retry tests | Continuous |
| QM-03 | Errors mapped in catalogue | 100% | < 100% | Catalogue audit | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | No stack traces to clients (ADR-D4-09) |
| Data classification touched | Internal |
| Personal data / PII | Error details redacted |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Error codes in audit/logs |
| Standards touched | ISO 9001, ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `src/pff_fa_ai/common/errors.py` |
| Configuration | Error catalogue |
| Contracts / schemas | Error fields |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-09, D3-18, D2-11 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All raised errors are PlatformError subclasses | Lint/audit |
| AC-02 | Only retryable errors retried | Retry tests |
| AC-03 | Every code in the catalogue | Catalogue audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Error rates by code/severity |
| Alerting | Severity-driven (ADR-D7-08) |
| Runbook | `docs/runbooks/errors.md` |
| Failure mode and degradation | Unmapped → generic INTERNAL with trace ref |
| Rollback | Catalogue revert |
| Support model impact | Backend + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Hierarchy + catalogue | S | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New error class recurs | Error review | Add subclass/code |
| RT-02 | Bad-retry incident | Incident | Fix retryable classification |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §51–§54, §58 |
| Requirement IDs | ERR-* |
| Build phases | 1 |
| Code paths | `src/pff_fa_ai/common/errors.py` |
| Configuration | error catalogue |
| Tests | retry + mapping suites |
| Upstream ADRs | ADR-D4-09 |
| Downstream ADRs | ADR-D7-06, D3-18, D7-08 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
