---
id: ADR-D6-18
title: Standards conformance — ISO/IEC 42001, 27001, 9001, NIST AI RMF, EU AI Act
domain: 6 Security & Governance
ws_ref: [WS-30]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Governance Lead
contributors: [Security Architect, Data Protection Officer, Quality Lead]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D6-13, ADR-D6-16, ADR-D6-17, ADR-D6-15, ADR-D0-01]
source_docs:
  - "MD files/5 QualityGovernance/20.PFF-FA-AI-GOVERNANCE.md §98, §99, §100"
build_phases: [12, 24]
impacted_paths:
  - docs/governance/
classification: Internal
review_due: 2027-08-22
---

# ADR-D6-18 — Standards conformance — ISO/IEC 42001, 27001, 9001, NIST AI RMF, EU AI Act

## 1. Summary

PFF AI will align to a defined set of standards — **ISO/IEC 42001 (AI management),
ISO/IEC 27001 (infosec), ISO/IEC 27701 (privacy), ISO 9001 (quality), ISO/IEC 23894 (AI
risk), NIST AI RMF, NIST CSF, and the EU AI Act / UK GDPR** — via a **compliance mapping**
that ties each requirement to the ADRs/controls that satisfy it, with evidence collected
continuously rather than at audit time (20.PFF-FA-AI-GOVERNANCE.md §98–§100). Conformance is treated as a
mapping-and-evidence exercise over the existing controls, not a parallel bureaucracy.

## 2. Context and Problem Statement

20.PFF-FA-AI-GOVERNANCE.md §98 lists the regulatory/compliance mapping (ISO/IEC 42001, 23894, 27001, 27701,
NIST AI RMF, NIST CSF), §99 compliance evidence, §100 compliance-mapping structure.
Without a single conformance decision and mapping, the platform cannot demonstrate
compliance efficiently and controls risk being built twice. This ADR fixes the target
standards and the mapping-driven conformance approach.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Define target standards | 20.PFF-FA-AI-GOVERNANCE.md §98 |
| DR-F-02 | Map requirements → ADRs/controls | 20.PFF-FA-AI-GOVERNANCE.md §100 |
| DR-F-03 | Continuous evidence collection | 20.PFF-FA-AI-GOVERNANCE.md §99 |
| DR-C-01 | Reuse existing controls (no parallel bureaucracy) | efficiency |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Existing ADRs cover most requirements | Add controls for gaps | Gap analysis |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Coverage of applicable standards | 28 | Compliance completeness | Mapping coverage |
| EC-02 | Evidence efficiency (continuous) | 22 | Audit-readiness | Evidence automation |
| EC-03 | Control reuse (no duplication) | 20 | Efficiency | Mapping vs new controls |
| EC-04 | Maintainability as standards evolve | 16 | EU AI Act evolving | Update ease |
| EC-05 | Cost/overhead | 14 | Sustainable | Effort |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Compliance mapping over existing ADRs/controls + continuous evidence

**Description.** A living mapping table: each standard's applicable requirements → the
ADR(s)/control(s) satisfying it → the evidence source (audit ADR-D6-17, eval, CI, config).
Evidence is collected continuously; gaps become new ADRs/controls.
**Strengths.** Complete, efficient, reuses controls, audit-ready.
**Weaknesses.** Mapping upkeep as standards/ADRs change.
**Cost / effort.** Medium.

### 5.2 Option B — Pursue formal certification first (e.g. ISO 42001 certification project)

**Description.** Run a certification programme up front.
**Strengths.** External assurance.
**Weaknesses.** Heavy, premature before the platform is built; certification follows
conformance, not precedes it.
**Cost / effort.** High; premature.

### 5.3 Option C — Standards as guidance only (no formal mapping/evidence)

**Description.** Keep standards in mind, no mapping.
**Strengths.** Low overhead.
**Weaknesses.** Can't demonstrate compliance; gaps invisible; 20.PFF-FA-AI-GOVERNANCE.md §99–§100 unmet.
**Cost / effort.** Low; non-compliant posture.

### 5.4 Option D — Adopt one framework only (e.g. ISO 42001) and ignore others

**Description.** Single-standard focus.
**Strengths.** Simpler.
**Weaknesses.** Misses infosec (27001), privacy (27701/GDPR), quality (9001), EU AI Act
obligations; 20.PFF-FA-AI-GOVERNANCE.md §98 lists several.
**Cost / effort.** Low; incomplete.

### 5.5 Option E — Compliance mapping + continuous evidence + periodic external gap assessment

**Description.** Option A plus periodic independent gap assessments to validate the
mapping and prepare for eventual certification.
**Strengths.** Ongoing external validation; certification-ready.
**Weaknesses.** Assessment cost.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No standards alignment | 20.PFF-FA-AI-GOVERNANCE.md §98 |
| Duplicate control set per standard | Inefficient; error-prone |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PFF-FA-AI-GOVERNANCE.md §98–§100.

| Criterion | Weight | A: Mapping+evidence | B: Certify first | C: Guidance only | D: One framework | E: A+gap assessment |
|---|---|---|---|---|---|---|
| EC-01 Coverage | 28 | 5 | 4 | 2 | 3 | 5 |
| EC-02 Evidence efficiency | 22 | 5 | 3 | 1 | 4 | 5 |
| EC-03 Control reuse | 20 | 5 | 3 | 3 | 4 | 5 |
| EC-04 Maintainability | 16 | 4 | 2 | 3 | 4 | 4 |
| EC-05 Cost | 14 | 4 | 1 | 5 | 4 | 3 |
| **Weighted total** | **100** | **472** | **288** | **266** | **376** | **472** |

Totals (×20): **A = 472**, **E = 472**, **D = 376**, **B = 288**, **C = 266**.

**Sensitivity.** A and E tie; periodic external gap assessment (E) adds independent
validation and certification-readiness for modest extra cost — adopted from the point the
platform reaches production maturity. A is the baseline mapping approach. Certify-first
(B) is premature; guidance-only (C) and single-framework (D) are insufficient.

## 7. Decision

**PFF AI will align to ISO/IEC 42001, 27001, 27701, 9001, 23894, NIST AI RMF, NIST CSF
and EU AI Act / UK GDPR via a living compliance mapping that ties each applicable
requirement to the satisfying ADRs/controls with continuously collected evidence, and
will add periodic independent gap assessments as the platform matures toward
certification-readiness (Option A now, Option E enhancement at production maturity).**
Certify-first (B), guidance-only (C) and single-framework (D) are rejected.

## 8. Architecture Detail

- A compliance mapping (20.PFF-FA-AI-GOVERNANCE.md §100) in `docs/governance/`: rows = requirements per
  standard; columns = satisfying ADR(s)/control(s), evidence source, status, owner.
- Evidence sources: audit store (ADR-D6-17), eval results (ADR-D7-13), CI gates, config
  audits, DPIA (ADR-D6-16), RAI metrics (ADR-D6-13).
- Gaps raise new ADRs/controls; the mapping is reviewed with change governance
  (ADR-D6-15) and the ADR programme (ADR-D0-01). EU AI Act risk categorisation tracked
  as it applies.

## 9. Consequences

### 9.1 Positive
- Demonstrable, efficient, multi-standard conformance built on existing controls.
### 9.2 Negative
- Mapping + evidence upkeep; assessment cost (E).
### 9.3 Neutral
- Ties RAI (D6-13), privacy (D6-16), audit (D6-17) together.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Up-front certification | Pragmatic, evidence-driven conformance | AI Governance Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Standards reinforce enterprise authority + accountability |
| Precedence chain | Reliability/accuracy standards uphold authoritative truth |
| Four-state separation | Privacy/infosec standards respect state boundaries |
| Versioned artefacts | Mapping + evidence versioned |
| Adam persona governs *how*, not *what* | Transparency standards: persona never misrepresents |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Compliance gap undetected | Med | High | H | Living mapping + gap assessment (E) | AI Governance Lead | Low |
| RSK-02 | Evidence not audit-ready | Med | Med | M | Continuous evidence (D6-17) | Governance | Low |
| RSK-03 | Standards evolve (EU AI Act) | Med | Med | M | Scheduled review; update mapping | AI Governance Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Applicable requirements mapped | 100% | < 100% | Mapping audit | Quarterly |
| QM-02 | Mapped requirements with current evidence | 100% | < 90% | Evidence audit | Quarterly |
| QM-03 | Open compliance gaps | 0 (or tracked) | untracked | Gap register | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | N/A (governance) |
| Data classification touched | Internal |
| Personal data / PII | 27701/GDPR alignment |
| Children's data and safeguarding | Covered via ADR-D6-16 mapping |
| UK GDPR lawful basis and rights impact | GDPR mapped explicitly |
| Audit and evidential requirements | Evidence model (ADR-D6-17) |
| Standards touched | ISO/IEC 42001, 27001, 27701, 9001, 23894; NIST AI RMF, CSF; EU AI Act; UK GDPR |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 12, 24 |
| Repository paths | `docs/governance/` (mapping) |
| Configuration | Compliance mapping table |
| Contracts / schemas | Requirement→control→evidence records |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D6-13, D6-16, D6-17, D6-15, D0-01 |
| Effort estimate | M (ongoing) |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Mapping covers all applicable requirements | Mapping audit |
| AC-02 | Each mapped requirement has evidence | Evidence audit |
| AC-03 | Gaps tracked with owners | Gap register |
| AC-04 | Gap assessment run at maturity | Assessment report |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Mapping coverage; evidence freshness |
| Alerting | Coverage/evidence gaps |
| Runbook | `docs/runbooks/compliance.md` |
| Failure mode and degradation | Gap → raise ADR/control |
| Rollback | N/A |
| Support model impact | Governance board |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Mapping + evidence tooling | M | small | Governance effort |
| External gap assessment (E) | — | periodic | Assessment fees |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Standard updated / EU AI Act obligations clarified | Compliance watch | Update mapping/controls |
| RT-02 | Certification pursued | Business | Run full Option E programme |

**Scheduled review:** `review_due` (and on standard changes).

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-30 Standards |
| Specification sections | 20.PFF-FA-AI-GOVERNANCE.md §98–§100 |
| Requirement IDs | GOV-STD-* |
| Build phases | 12, 24 |
| Code paths | `docs/governance/` |
| Configuration | compliance mapping |
| Tests | mapping/evidence audits |
| Upstream ADRs | ADR-D6-13, D6-16, D6-17 |
| Downstream ADRs | ADR-D6-15, D0-01 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Governance Lead | Initial decision recorded. |
