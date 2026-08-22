---
id: ADR-D4-09
title: Metadata, response envelope and error-code standards
domain: 4 Information
ws_ref: [WS-21]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [AI Architecture Lead, API Designer, SRE]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D2-15, ADR-D7-03, ADR-D7-05, ADR-D2-04, ADR-D2-17]
source_docs:
  - "MD files/3 Context & Integration/10 PF-FT-AI-ENTERPRISE-INTEGRATION.md §16, §19, §20, §38, §39, §40, §84"
  - "MD files/2 Agent Runtime/6 PF-FT-AI-CONVERSATION-SESSION.md §76"
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md"
build_phases: [2, 5]
impacted_paths:
  - src/pf_ft_ai/api/
  - src/pf_ft_ai/common/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-09 — Metadata, response envelope and error-code standards

## 1. Summary

PFF AI will use a **single standard response envelope** for its API — a typed
Pydantic structure carrying `data`, a `metadata` block (correlation id, timestamps,
versions, pagination) and a structured `error` block with a **stable, namespaced
error-code taxonomy** aligned to the `PlatformError` hierarchy — so every client and
log sees a consistent shape (doc 10 §19–§20, §38–§40, §84; doc 6 §76; CLAUDE.md
exception hierarchy). Errors are translated at the boundary; internal exceptions never
leak raw.

## 2. Context and Problem Statement

Doc 10 §19–§20 define response contract/payload, §38–§40 define the tool/error
contract, error translation and error categories, §84 defines the correlation id;
doc 6 §76 defines the conversation API contract; CLAUDE.md fixes the `PlatformError`
subclass hierarchy (`ValidationError`, `IntegrationError`, `ToolError`, …). Without a
single envelope and error-code standard, each endpoint invents its own shape,
correlation is inconsistent, clients special-case errors, and internal stack traces
leak. This ADR fixes the wire contract and error taxonomy.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | One response envelope (data/metadata/error) | doc 10 §19–§20; doc 6 §76 |
| DR-F-02 | Stable namespaced error codes ↔ PlatformError | doc 10 §38–§40; CLAUDE.md |
| DR-F-03 | Correlation id + versions in metadata | doc 10 §84; ADR-D7-03 |
| DR-C-01 | No raw internal exceptions to clients | doc 10 §39 |
| DR-F-04 | Consistent pagination metadata | doc 10 §20 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | One envelope suits chat + admin APIs | Envelope variants per API family | API review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Consistency across endpoints | 26 | Client simplicity; observability | One shape? |
| EC-02 | Error clarity & stability | 24 | Clients rely on codes | Stable code set |
| EC-03 | Observability (correlation/versions) | 20 | Tracing/debugging | Metadata present |
| EC-04 | Security (no leakage) | 16 | No stack traces out | Redaction |
| EC-05 | Simplicity/adoption | 14 | Devs follow it | Boilerplate |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Single typed envelope {data, metadata, error} + namespaced error codes ↔ PlatformError

**Description.** One Pydantic envelope; metadata block with correlation id, timestamps,
api/schema versions, pagination; error block with `code` (e.g. `PFF.VALIDATION.xxx`),
`message`, `details`, `retriable`; boundary translates `PlatformError` subclasses to
codes; raw exceptions never serialized.
**Strengths.** Consistent, observable, secure, stable.
**Weaknesses.** Envelope boilerplate.
**Cost / effort.** Low-medium.

### 5.2 Option B — Bare payloads, HTTP status only for errors

**Description.** Return data directly; use HTTP codes for errors.
**Strengths.** Minimal.
**Weaknesses.** No structured error detail; no metadata/correlation in body; clients
can't distinguish error subtypes; poor observability.
**Cost / effort.** Low; weak.

### 5.3 Option C — RFC 7807 problem+json for errors, bare data for success

**Description.** Standard problem-details for errors; plain data otherwise.
**Strengths.** Standard error format.
**Weaknesses.** Asymmetric (success vs error shapes differ); success responses lack
the metadata block; still need our code taxonomy inside it.
**Cost / effort.** Low-medium; partial.

### 5.4 Option D — GraphQL-style {data, errors[]} envelope

**Description.** Data plus an errors array.
**Strengths.** Multiple errors; single shape.
**Weaknesses.** Partial-success semantics add complexity for a mostly-REST chat API;
overkill; still need code taxonomy.
**Cost / effort.** Medium.

### 5.5 Option E — Per-API-family envelopes (chat vs admin vs internal)

**Description.** Different envelopes per API family.
**Strengths.** Tailored per audience.
**Weaknesses.** Inconsistency; more to learn/maintain; correlation/versions duplicated
differently.
**Cost / effort.** Medium; fragmenting.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Leak internal exception messages | DR-C-01/doc 10 §39 |
| Ad-hoc per-endpoint shapes | EC-01 — inconsistency |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 10 §19–§20/§38–§40/§84, doc
6 §76 and the PlatformError hierarchy.

| Criterion | Weight | A: Unified envelope | B: Bare+HTTP | C: RFC7807 errors | D: GraphQL-style | E: Per-family |
|---|---|---|---|---|---|---|
| EC-01 Consistency | 26 | 5 | 2 | 3 | 4 | 2 |
| EC-02 Error clarity | 24 | 5 | 2 | 4 | 4 | 3 |
| EC-03 Observability | 20 | 5 | 2 | 3 | 4 | 3 |
| EC-04 Security | 16 | 5 | 3 | 4 | 4 | 4 |
| EC-05 Simplicity | 14 | 4 | 5 | 4 | 3 | 3 |
| **Weighted total** | **100** | **484** | **256** | **356** | **384** | **294** |

Totals (×20): **A = 484**, **D = 384**, **C = 356**, **E = 294**, **B = 256**.

**Sensitivity.** A leads D by 100. A can adopt RFC 7807-compatible fields *inside* its
error block (interoperability) without giving up the symmetric metadata block — so
C's benefit is absorbed. No re-weighting favours the fragmenting options.

## 7. Decision

**PFF AI will use a single typed response envelope `{data, metadata, error}` with a
namespaced, stable error-code taxonomy mapped from the `PlatformError` hierarchy, a
metadata block carrying correlation id, timestamps, api/schema versions and
pagination, and boundary error-translation that never serializes raw internal
exceptions (Option A).** The error block is RFC 7807-compatible in its field names for
interoperability. Bare payloads (B), asymmetric problem-json (C), GraphQL-style (D)
and per-family envelopes (E) are rejected.

**Status rationale.** `Accepted` — doc 10 §19–§40 and CLAUDE.md govern this.

## 8. Architecture Detail

- `src/pf_ft_ai/common/envelope.py`: `ApiResponse[T]{data: T | None, metadata:
  ResponseMetadata, error: ApiError | None}`.
- `ResponseMetadata`: `correlation_id` (doc 10 §84; ADR-D7-03), `timestamp`,
  `api_version`, `schema_version`, `pagination` (§20).
- `ApiError`: `code` (`PFF.<CATEGORY>.<NAME>`), `message` (safe), `details`,
  `retriable`, `trace_ref`.
- Error translation: a boundary handler maps each `PlatformError` subclass (CLAUDE.md)
  to a category/code (doc 10 §39–§40); unexpected exceptions map to a generic
  `PFF.INTERNAL.UNEXPECTED` with a trace ref, never a stack trace.
- Event envelope (ADR-D2-17) shares the metadata conventions where applicable.

## 9. Consequences

### 9.1 Positive
- One shape for clients and logs; stable error contract; strong correlation.
### 9.2 Negative
- Envelope wrapping boilerplate (mitigated by helpers/decorators).
### 9.3 Neutral
- Aligns with error taxonomy (ADR-D7-05) and correlation (ADR-D7-03).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Bare-payload minimalism | Consistency, observability, security | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Envelope carries results; no business authority |
| Precedence chain | Metadata can carry source/authority where relevant |
| Four-state separation | Wire contract only; no state conflation |
| Versioned artefacts | api/schema versions in metadata |
| Adam persona governs *how*, not *what* | Error messages factual; persona wording separate |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Internal exception leaks to client | Low | High | M | Boundary translation + tests (§39) | Backend Lead | Low |
| RSK-02 | Error codes churn, breaking clients | Med | Med | M | Stable code registry + deprecation policy | API Designer | Low |
| RSK-03 | Missing correlation id | Low | Med | M | Middleware enforces id (ADR-D7-03) | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Responses using standard envelope | 100% | < 100% | Contract tests | Per release |
| QM-02 | Raw-exception leaks | 0 | > 0 | Security tests | Continuous |
| QM-03 | Correlation id present | 100% | < 100% | Logs | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Error translation prevents info leakage |
| Data classification touched | Internal |
| Personal data / PII | Error details must not carry PII (redaction) |
| Children's data and safeguarding | No safeguarding data in error payloads |
| UK GDPR lawful basis and rights impact | Minimises incidental data exposure |
| Audit and evidential requirements | Correlation id ties logs to requests |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 (API), 5 (integration errors) |
| Repository paths | `src/pf_ft_ai/api/`, `src/pf_ft_ai/common/` |
| Configuration | Error-code registry |
| Contracts / schemas | Envelope + error models |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D2-15, ADR-D7-03, ADR-D7-05 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All endpoints return the envelope | Contract test |
| AC-02 | PlatformError subclasses map to stable codes | Unit test |
| AC-03 | No raw exception serialized | Security test |
| AC-04 | Correlation id + versions present | Middleware test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Error-code distribution; correlation coverage |
| Alerting | Spike in INTERNAL errors |
| Runbook | `docs/runbooks/api-errors.md` |
| Failure mode and degradation | Consistent error envelope on failures |
| Rollback | Envelope/version revert |
| Support model impact | Backend + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Envelope + error registry | S | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New API family needs different shape | API review | Consider variant (Option E) narrowly |
| RT-02 | Error-code churn breaks clients | QM-02/feedback | Tighten deprecation policy |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-21 Metadata/Envelope |
| Specification sections | doc 10 §16, §19–§20, §38–§40, §84; doc 6 §76; doc 24 |
| Requirement IDs | API-ENV-* |
| Build phases | 2, 5 |
| Code paths | `src/pf_ft_ai/api/`, `src/pf_ft_ai/common/` |
| Configuration | error-code registry |
| Tests | envelope + error contract suites |
| Upstream ADRs | ADR-D2-15 |
| Downstream ADRs | ADR-D7-03, ADR-D7-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
