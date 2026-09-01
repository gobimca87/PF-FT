---
id: ADR-D6-16
title: UK GDPR, safeguarding and children's-data handling
domain: 6 Security & Governance
ws_ref: [WS-29]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Data Protection Officer
contributors: [Security Architect, AI Governance Lead, Safeguarding Lead]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-07, ADR-D6-06, ADR-D6-07, ADR-D6-12, ADR-D6-17]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §31, §32, §33, §34"
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §26, §98"
build_phases: [9, 12]
impacted_paths:
  - docs/governance/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-16 — UK GDPR, safeguarding and children's-data handling

## 1. Summary

Because FA football data pervasively involves **children and safeguarding**, PFF AI
treats children's personal data and safeguarding information as **special-category-grade,
most-protected data**: lawful-basis-aware, minimised, never sent to external models
(ADR-D6-07), ACL-restricted (ADR-D6-12), retained only as needed, subject to a **DPIA**,
and never used to profile or make automated significant decisions about a child (19.PF-FT-AI-SECURITY.md
§31–§34; 20.PF-FT-AI-GOVERNANCE.md §26, §98; UK GDPR). Where the spec is silent, this ADR mandates a DPIA to
close the gap.

## 2. Context and Problem Statement

19.PF-FT-AI-SECURITY.md §31–§34 cover PII/classification/data-flow/minimisation; 20.PF-FT-AI-GOVERNANCE.md §26 privacy, §98
regulatory mapping (incl. ISO 27701). The spec does not contain a dedicated children's-
data/safeguarding section, yet the FA domain (players, many minors; officials;
safeguarding records) makes this the single highest-consequence privacy area. Leaving it
implicit risks a serious breach and regulatory/safeguarding failure. This ADR fixes the
handling rules and mandates a DPIA.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Children's/safeguarding data = most protected | UK GDPR; domain reality |
| DR-C-02 | Lawful basis + minimisation + retention | 19.PF-FT-AI-SECURITY.md §34; UK GDPR Art. 5–6 |
| DR-C-03 | No external-model egress of such data | ADR-D6-07 |
| DR-C-04 | No profiling/automated significant decisions on children | UK GDPR Art. 22; ADR-D1-02 |
| DR-F-01 | DPIA for the platform | ICO guidance |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise (PFF) is controller; AI is processor for these data | Clarify roles in DPIA | DPO/legal |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Protection of children's/safeguarding data | 34 | Highest consequence | Controls in place |
| EC-02 | Lawful-basis & minimisation compliance | 22 | UK GDPR | Compliance evidence |
| EC-03 | No prohibited processing (profiling) | 18 | Art. 22 | Boundary tests |
| EC-04 | Rights handling (access/erasure) | 14 | Data-subject rights | Rights flow |
| EC-05 | Practicality | 12 | Workable | Overhead |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Treat children's/safeguarding data as most-protected: minimise, no external egress, ACL, retention limits, DPIA, no profiling

**Description.** Classify as special-category-grade (ADR-D4-07); minimise (ADR-D6-06);
block external-model egress (ADR-D6-07); ACL-restrict knowledge (ADR-D6-12); strict
retention/erasure; DPIA before go-live; explicit no-profiling/no-automated-significant-
decision rule.
**Strengths.** Comprehensive, compliant, safeguarding-first.
**Weaknesses.** Constrains some features (by design).
**Cost / effort.** Medium.

### 5.2 Option B — Standard PII handling (no special children's treatment)

**Description.** Treat all PII the same.
**Strengths.** Simpler.
**Weaknesses.** Under-protects children's/special-category data; non-compliant.
**Cost / effort.** Low; unacceptable.

### 5.3 Option C — Exclude children's data from the platform entirely

**Description.** Don't process any children's data.
**Strengths.** Removes the risk.
**Weaknesses.** Infeasible — affiliation/registration inherently involves minors;
guts core workflows.
**Cost / effort.** Low; impractical.

### 5.4 Option D — Anonymise/aggregate children's data before any AI processing

**Description.** Only process anonymised/aggregated data.
**Strengths.** Strong privacy.
**Weaknesses.** Many workflows need identified records (a specific child's registration);
anonymisation breaks them. Useful for analytics, not transactional flows.
**Cost / effort.** Medium; partial applicability.

### 5.5 Option E — Option A + consent/age-appropriate-design + regular safeguarding review board sign-off

**Description.** Option A plus age-appropriate-design-code alignment and a safeguarding
review board that signs off relevant changes.
**Strengths.** Strongest safeguarding governance.
**Weaknesses.** More governance overhead.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Send children's data to external SLM | ADR-D6-07; UK GDPR |
| Automated eligibility decisions on a child without human oversight | Art. 22; ADR-D6-14 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 19.PF-FT-AI-SECURITY.md §31–§34, 20.PF-FT-AI-GOVERNANCE.md §26/§98 and
UK GDPR/ICO age-appropriate design.

| Criterion | Weight | A: Most-protected | B: Standard PII | C: Exclude | D: Anonymise-only | E: A+safeguarding board |
|---|---|---|---|---|---|---|
| EC-01 Child protection | 34 | 5 | 2 | 5 | 4 | 5 |
| EC-02 Lawful basis/minimisation | 22 | 5 | 3 | 3 | 4 | 5 |
| EC-03 No prohibited processing | 18 | 5 | 3 | 5 | 4 | 5 |
| EC-04 Rights handling | 14 | 5 | 3 | 2 | 3 | 5 |
| EC-05 Practicality | 12 | 4 | 5 | 1 | 2 | 3 |
| **Weighted total** | **100** | **488** | **300** | **384** | **370** | **492** |

Totals (×20): **E = 492**, **A = 488**, **C = 384**, **D = 370**, **B = 300**.

**Sensitivity.** E (A + safeguarding board + age-appropriate design) edges A given the
consequence level; a safeguarding review board sign-off for relevant changes is
proportionate to the risk. Exclusion (C) is impractical; standard PII (B) is
non-compliant. Anonymisation (D) suits analytics, not transactional workflows.

## 7. Decision

**PFF AI will treat children's personal data and safeguarding information as
most-protected, special-category-grade data: minimised, never egressed to external
models, ACL-restricted, retention-limited, with lawful-basis awareness, no profiling or
automated significant decisions about a child without human oversight, a mandatory DPIA
before go-live, alignment with the ICO Age-Appropriate Design Code, and a safeguarding
review board sign-off for relevant changes (Option E).** Standard-PII treatment (B),
exclusion (C) and anonymise-only (D) are rejected. Where the source spec is silent, this
ADR is the governing requirement.

## 8. Architecture Detail

- Classification: children's/safeguarding data marked special-category (ADR-D4-07),
  driving strictest controls: minimisation (ADR-D6-06), external-egress block
  (ADR-D6-07), ACL (ADR-D6-12), encryption/CMK (ADR-D6-05), audit (ADR-D6-17).
- No-profiling rule: the platform makes no automated significant decision about a child;
  such decisions are enterprise/HIL (ADR-D6-14, D1-02).
- DPIA maintained in `docs/governance/`; rights (access/erasure/rectification) routed to
  the enterprise system of record (PFF as controller); retention limits enforced (9 PF-FT-AI-MEMORY-CACHE.md
  §75).
- Safeguarding review board sign-off wired into change governance (ADR-D6-15) for
  relevant changes.

## 9. Consequences

### 9.1 Positive
- Strong, compliant, safeguarding-first handling of the highest-risk data.
### 9.2 Negative
- Feature constraints + governance overhead (accepted).
### 9.3 Neutral
- Concretises D4-07/D6-06/D6-07/D6-12 for children's data.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some feature latitude with children's data | Safeguarding + compliance | DPO, Safeguarding Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Significant decisions about children stay with enterprise/humans |
| Precedence chain | Children's records are authoritative enterprise data, referenced not copied |
| Four-state separation | Children's data confined to most-protected handling |
| Versioned artefacts | Handling policy + DPIA versioned |
| Adam persona governs *how*, not *what* | Persona never exposes/among children's data inappropriately |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Children's data breach/egress | Low | Critical | H | Egress block + ACL + encryption + audit | DPO | Low |
| RSK-02 | Automated decision harms a child | Low | Critical | H | No-profiling rule + HIL (ADR-D6-14) | Safeguarding Lead | Low |
| RSK-03 | Non-compliance (no DPIA) | Low | High | M | Mandatory DPIA before go-live | DPO | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Children's data egress to external model | 0 | > 0 | Boundary tests | Continuous |
| QM-02 | Automated significant decisions on children | 0 | > 0 | Workflow audit | Continuous |
| QM-03 | DPIA current | yes | overdue | Governance | Annual |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Strictest controls on highest-risk data |
| Data classification touched | Special-category / children's |
| Personal data / PII | Children's PII most-protected |
| Children's data and safeguarding | This ADR is the governing decision |
| UK GDPR lawful basis and rights impact | Lawful basis, minimisation, rights, DPIA, Art. 22 |
| Audit and evidential requirements | Full audit (ADR-D6-17) |
| Standards touched | UK GDPR, ISO/IEC 27701, ICO Age-Appropriate Design Code |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 9, 12 |
| Repository paths | `docs/governance/` (DPIA) + controls |
| Configuration | Special-category classification rules |
| Contracts / schemas | Retention/rights records |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-07, D6-06, D6-07, D6-12, D6-14 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Children's data never egresses externally | Boundary tests |
| AC-02 | No automated significant decision on a child | Workflow audit |
| AC-03 | DPIA completed before go-live | Governance gate |
| AC-04 | Retention/erasure enforced | Data tests |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Access to children's data; egress attempts |
| Alerting | Any egress/breach (sev-1) |
| Runbook | `docs/runbooks/safeguarding-data.md` |
| Failure mode and degradation | Uncertain → treat as children's/special-category |
| Rollback | Policy revert |
| Support model impact | DPO + safeguarding board |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| DPIA + controls + board | M | small | Governance effort |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New processing of children's data | Change intake | New/updated DPIA |
| RT-02 | Safeguarding/data incident | Incident | CAR; board review |

**Scheduled review:** `review_due` (and at any new children's-data processing).

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-29 Compliance/Safeguarding |
| Specification sections | 19.PF-FT-AI-SECURITY.md §31–§34; 20.PF-FT-AI-GOVERNANCE.md §26, §98 |
| Requirement IDs | GOV-CHILD-* |
| Build phases | 9, 12 |
| Code paths | governance + controls |
| Configuration | special-category rules |
| Tests | egress + decision + retention suites |
| Upstream ADRs | ADR-D4-07, D6-06, D6-07 |
| Downstream ADRs | ADR-D6-12, D6-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Data Protection Officer | Initial decision recorded. |
