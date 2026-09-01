---
id: ADR-D4-05
title: ERC partial-failure semantics — mandatory vs optional, completeness tracking
domain: 4 Information
ws_ref: [WS-19]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Integration Engineer, SRE]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-04, ADR-D4-02, ADR-D2-11, ADR-D3-08, ADR-D2-12]
source_docs:
  - "MD files/3 Context & Integration/8 PF-FT-AI-ERC-CONTEXT.md §24, §44, §45, §46, §47, §48, §49, §50, §51, §52, §71, §72, §73"
  - "MD files/1 Foundation/5. PF-FT-AI-STATE-MODEL.md §66"
build_phases: [4]
impacted_paths:
  - src/pf_ft_ai/erc/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-05 — ERC partial-failure semantics — mandatory vs optional, completeness tracking

## 1. Summary

PFF AI will classify every context requirement as **mandatory** or **optional** and
handle partial ERC-collection failures accordingly: a failed **mandatory** collection
**fails the ERC build** (the workflow cannot safely proceed), while a failed
**optional** collection degrades gracefully with the gap recorded in an explicit
**completeness** structure (8 PF-FT-AI-ERC-CONTEXT.md §24, §44–§52, §71–§73). The platform never silently
proceeds on incomplete authoritative context, and never fabricates the missing piece.

## 2. Context and Problem Statement

8 PF-FT-AI-ERC-CONTEXT.md §24 distinguishes mandatory vs optional context; §44–§48 define batch state,
retry and partial-batch failure; §49–§50 define mandatory- vs optional-collection
failure; §51–§52 define completeness tracking and record completeness; §71–§73 define
the ERC validation result with warnings/errors; 5. PF-FT-AI-STATE-MODEL.md §66 covers partial completion.
The hazard: a collection partially fails (e.g. one official's record errors), and the
platform either aborts a workflow that could proceed on optional data, or worse,
proceeds on missing *mandatory* data and makes an unsafe decision. This ADR fixes the
semantics.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Mandatory vs optional per requirement | 8 PF-FT-AI-ERC-CONTEXT.md §24 |
| DR-F-02 | Mandatory failure → fail build; optional → degrade + record | 8 PF-FT-AI-ERC-CONTEXT.md §49–§50 |
| DR-F-03 | Completeness tracked and surfaced | 8 PF-FT-AI-ERC-CONTEXT.md §51–§52 |
| DR-C-01 | Never proceed on missing mandatory context | 8 PF-FT-AI-ERC-CONTEXT.md §49; CLAUDE.md |
| DR-C-02 | Never fabricate missing data | CLAUDE.md; 8 PF-FT-AI-ERC-CONTEXT.md §71–§73 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Requirements can be classified mandatory/optional up front | Default to mandatory (fail-safe) | Requirement review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Safety (no proceed on missing mandatory) | 32 | Correctness of decisions | Fail-on-mandatory tests |
| EC-02 | Graceful degradation on optional | 22 | Availability | Degrade+record works |
| EC-03 | Transparency (completeness surfaced) | 20 | Trust/auditability | Completeness present |
| EC-04 | Retry effectiveness | 14 | Transient recovery | Recovery rate |
| EC-05 | Simplicity | 12 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Mandatory/optional classification + fail-on-mandatory + degrade-and-record optional + bounded retry

**Description.** Each requirement classified; collection failures retried within
limits (§46–§47); on exhaustion, mandatory failure fails the ERC (§49) and the
workflow suspends/errors safely (ADR-D2-11/D3-08); optional failure degrades and is
recorded in the completeness structure (§51) with an ERC warning (§72).
**Strengths.** Safe, available, transparent.
**Weaknesses.** Requires classification discipline.
**Cost / effort.** Low-medium.

### 5.2 Option B — All-or-nothing (any failure fails ERC)

**Description.** Any collection failure aborts.
**Strengths.** Simple; safe.
**Weaknesses.** Poor availability — a non-essential gap blocks the whole workflow.
**Cost / effort.** Low; brittle UX.

### 5.3 Option C — Best-effort (proceed with whatever succeeded)

**Description.** Use whatever collected; ignore gaps.
**Strengths.** Max availability.
**Weaknesses.** Can proceed on missing mandatory data → unsafe decisions; violates
DR-C-01.
**Cost / effort.** Low; dangerous.

### 5.4 Option D — Proceed with placeholder/inferred values for gaps

**Description.** Fill missing data with defaults/inference.
**Strengths.** Keeps flowing.
**Weaknesses.** Fabrication of authoritative data — hard prohibition (CLAUDE.md).
**Cost / effort.** Low; unacceptable.

### 5.5 Option E — Mandatory/optional + severity tiers (critical/important/nice-to-have)

**Description.** Finer than binary: multiple severity levels driving different
behaviours.
**Strengths.** Nuanced degradation.
**Weaknesses.** More complexity; 8 PF-FT-AI-ERC-CONTEXT.md frames it as mandatory/optional; extra tiers
add classification burden for marginal benefit now.
**Cost / effort.** Medium; premature nuance.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Silent proceed on partial | DR-C-01/transparency |
| Infinite retry | ADR-D2-11 — bounded retries |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 8 PF-FT-AI-ERC-CONTEXT.md §24/§44–§52/§71–§73 and
5. PF-FT-AI-STATE-MODEL.md §66.

| Criterion | Weight | A: Mand/opt + degrade | B: All-or-nothing | C: Best-effort | D: Placeholder | E: Severity tiers |
|---|---|---|---|---|---|---|
| EC-01 Safety | 32 | 5 | 5 | 1 | 1 | 5 |
| EC-02 Graceful degradation | 22 | 5 | 1 | 5 | 4 | 5 |
| EC-03 Transparency | 20 | 5 | 3 | 1 | 1 | 5 |
| EC-04 Retry | 14 | 5 | 3 | 3 | 3 | 5 |
| EC-05 Simplicity | 12 | 4 | 5 | 4 | 4 | 3 |
| **Weighted total** | **100** | **488** | **336** | **242** | **222** | **476** |

Totals (×20): **A = 488**, **E = 476**, **B = 336**, **C = 242**, **D = 222**.

**Sensitivity.** A edges E by 12; severity tiers (E) are a possible future refinement
(RT-01) but add classification burden now. B sacrifices availability; C/D are unsafe.

## 7. Decision

**PFF AI will classify context requirements as mandatory or optional; a failed
mandatory collection (after bounded retry) fails the ERC build and the workflow
suspends or errors safely, while a failed optional collection degrades gracefully and
is recorded in an explicit completeness structure with an ERC warning (Option A).**
The platform never proceeds on missing mandatory context and never fabricates missing
data. Unclassified requirements default to mandatory (fail-safe). All-or-nothing (B)
harms availability; best-effort (C) and placeholder (D) are unsafe; severity tiers (E)
are deferred.

**Status rationale.** `Accepted` — 8 PF-FT-AI-ERC-CONTEXT.md §49–§52 govern this.

## 8. Architecture Detail

- Requirement model (8 PF-FT-AI-ERC-CONTEXT.md §23) carries `mandatory: bool`; collection results roll up
  into a `Completeness` structure (§51–§52) per section and record.
- Retry within limits (§46–§47) using the shared client's policy (ADR-D5-16); on
  exhaustion, branch by mandatory/optional (§49–§50).
- Mandatory failure → ERC validation `error` (§73) → workflow suspend/error
  (ADR-D2-11), with an honest user message (ADR-D3-08) — never a fabricated proceed.
- Optional failure → ERC `warning` (§72); the completeness structure is available to
  consumers and surfaced in traces.

## 9. Consequences

### 9.1 Positive
- Safe on mandatory gaps, available on optional gaps, transparent throughout.
### 9.2 Negative
- Requirement classification effort.
### 9.3 Neutral
- Completeness data feeds observability and eval.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of all-or-nothing | Availability + safety balance | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Missing authoritative context blocks unsafe AI action |
| Precedence chain | Never substitutes lower-authority/fabricated data for missing enterprise data |
| Four-state separation | Completeness tracked on the ERC (enterprise-reference) plane |
| Versioned artefacts | Classification config versioned |
| Adam persona governs *how*, not *what* | Persona reports gaps honestly (no fabrication) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Mandatory mis-classified as optional | Low | High | M | Default-mandatory; review | AI Arch Lead | Low |
| RSK-02 | Transient failure fails a workflow | Med | Med | M | Bounded retry/backoff first | SRE | Low |
| RSK-03 | Completeness gaps ignored downstream | Low | Med | M | Consumers must check completeness; tests | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Proceed-on-missing-mandatory incidents | 0 | > 0 | Tests/audit | Continuous |
| QM-02 | Optional-failure graceful-degrade rate | 100% | < 100% | Traces | Continuous |
| QM-03 | Transient failures recovered by retry | tracked | falling | Metrics | Weekly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None new |
| Data classification touched | As per sections |
| Personal data / PII | No fabrication of personal data |
| Children's data and safeguarding | Missing safeguarding data blocks unsafe proceed |
| UK GDPR lawful basis and rights impact | Accuracy principle upheld (no invented data) |
| Audit and evidential requirements | Completeness recorded |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4 |
| Repository paths | `src/pf_ft_ai/erc/` |
| Configuration | Requirement mandatory/optional map; retry limits |
| Contracts / schemas | Completeness + validation-result models (§71–§73) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-04, ADR-D2-11, ADR-D3-08 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Mandatory failure fails ERC/suspends workflow | Fault-injection test |
| AC-02 | Optional failure degrades + records completeness | Test |
| AC-03 | No fabricated/placeholder data on gaps | Code + test |
| AC-04 | Unclassified defaults to mandatory | Unit test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Mandatory-fail rate; optional-degrade rate; completeness |
| Alerting | Mandatory-failure spikes |
| Runbook | `docs/runbooks/erc.md` |
| Failure mode and degradation | Defined by mandatory/optional branching |
| Rollback | Classification/retry config revert |
| Support model impact | Integration + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Failure-handling + completeness | M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Binary classification too coarse | Ops feedback | Consider severity tiers (Option E) |
| RT-02 | Mandatory failures frequent for one source | QM-01/metrics | Improve source resilience / reclassify |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-19 |
| Specification sections | 8 PF-FT-AI-ERC-CONTEXT.md §24, §44–§52, §71–§73; 5. PF-FT-AI-STATE-MODEL.md §66 |
| Requirement IDs | ERC-FAIL-* |
| Build phases | 4 |
| Code paths | `src/pf_ft_ai/erc/` |
| Configuration | mandatory/optional map, retry limits |
| Tests | partial-failure + completeness suites |
| Upstream ADRs | ADR-D4-04 |
| Downstream ADRs | ADR-D2-11, ADR-D3-08 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
