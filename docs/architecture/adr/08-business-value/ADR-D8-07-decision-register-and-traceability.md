---
id: ADR-D8-07
title: Decision register and end-to-end traceability model
domain: 8 Business Value
ws_ref: [WS-36]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [AI Governance Lead, Programme Manager]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D0-01, ADR-D0-02, ADR-D1-12, ADR-D8-06, ADR-D6-18]
source_docs:
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §29, §115, §116"
build_phases: [21]
impacted_paths:
  - docs/architecture/adr/_register/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-07 — Decision register and end-to-end traceability model

## 1. Summary

PFF AI will maintain a **decision register and a traceability matrix** linking every ADR to
its WS sheet, source-doc sections, requirement IDs (ADR-D1-12), build phases, code paths and
related decisions — so any decision can be traced from business need to implementation and
back (20.PF-FT-AI-GOVERNANCE.md §29, §115–§116). This ADR governs the `_register/` artefacts created by the ADR
programme (ADR-D0-01).

## 2. Context and Problem Statement

20.PF-FT-AI-GOVERNANCE.md §29 traceability, §115 governance traceability matrix, §116 governance DoD. The ADR
library holds 136 decisions across 8 domains; without a register + traceability matrix,
navigating and auditing them (and proving requirement coverage) is impractical. This ADR
fixes the decision register and traceability model.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Central decision register (all ADRs) | 20.PF-FT-AI-GOVERNANCE.md §115; ADR-D0-01 |
| DR-F-02 | Traceability: WS↔doc↔req↔phase↔code | 20.PF-FT-AI-GOVERNANCE.md §29, §115 |
| DR-F-03 | Bidirectional (need→impl and back) | traceability practice |
| DR-C-01 | Kept current with the ADR library | ADR-D0-02 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Register can be kept in sync | Auto-generate from front matter | Tooling |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Traceability completeness | 30 | Audit/coverage | Links present |
| EC-02 | Currency (stays in sync) | 24 | Trust | Sync method |
| EC-03 | Navigability | 18 | Usability | Findability |
| EC-04 | Requirement coverage proof | 16 | Nothing unaddressed | Coverage map |
| EC-05 | Overhead | 12 | Sustainable | Upkeep |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Decision register + traceability matrix auto-generated from ADR front matter

**Description.** A register (id, title, domain, status, owner, WS, source-docs) and a
traceability matrix (ADR↔WS↔doc§↔requirement↔phase↔code) generated from each ADR's YAML front
matter, so they stay in sync automatically; bidirectional links.
**Strengths.** Complete, current, navigable, coverage-provable, low manual effort.
**Weaknesses.** Generation tooling.
**Cost / effort.** Low-medium.

### 5.2 Option B — Manually maintained register/matrix

**Description.** Hand-edit the registers.
**Strengths.** No tooling.
**Weaknesses.** Drifts out of sync; error-prone at 136 ADRs.
**Cost / effort.** Low start, high drift.

### 5.3 Option C — Register only (no traceability matrix)

**Description.** List ADRs; no cross-links.
**Strengths.** Simple.
**Weaknesses.** No requirement/phase/code traceability; weak audit.
**Cost / effort.** Low; incomplete.

### 5.4 Option D — External GRC/ALM tool for traceability

**Description.** Traceability in a dedicated tool.
**Strengths.** Rich features.
**Weaknesses.** Split from in-repo ADRs; sync overhead; over-tooled now.
**Cost / effort.** Medium.

### 5.5 Option E — Auto-generated register/matrix + CI validation (broken-link + coverage checks)

**Description.** Option A with CI checks that every ADR link resolves, every requirement maps
to ≥1 ADR, and status/register consistency holds (verification checks per the plan).
**Strengths.** A + enforced integrity + coverage proof.
**Weaknesses.** CI check upkeep.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No register | 20.PF-FT-AI-GOVERNANCE.md §115; ADR-D0-01 |
| Traceability by memory | Unauditable |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PF-FT-AI-GOVERNANCE.md §29/§115–§116 and the ADR
programme (ADR-D0-01/02).

| Criterion | Weight | A: Auto-gen | B: Manual | C: Register-only | D: External tool | E: Auto-gen+CI |
|---|---|---|---|---|---|---|
| EC-01 Completeness | 30 | 5 | 3 | 2 | 5 | 5 |
| EC-02 Currency | 24 | 5 | 2 | 3 | 3 | 5 |
| EC-03 Navigability | 18 | 4 | 4 | 3 | 4 | 5 |
| EC-04 Coverage proof | 16 | 4 | 2 | 1 | 4 | 5 |
| EC-05 Overhead | 12 | 4 | 3 | 5 | 2 | 4 |
| **Weighted total** | **100** | **456** | **282** | **266** | **388** | **496** |

Totals (×20): **E = 496**, **A = 456**, **D = 388**, **B = 282**, **C = 266**.

**Sensitivity.** E (auto-gen + CI validation) wins by enforcing link integrity and
requirement coverage — exactly the verification the ADR programme needs at 136 ADRs. Adopted.
Manual (B) drifts; register-only (C) can't prove coverage.

## 7. Decision

**PFF AI will maintain a decision register and a traceability matrix auto-generated from ADR
front matter, with CI validation of link integrity, status/register consistency and
requirement coverage (Option E).** These are the `_register/` artefacts of the ADR programme
(ADR-D0-01). Manual maintenance (B), register-only (C) and external-tool-only (D) are
rejected.

## 8. Architecture Detail

- `_register/decision-register.md` (id, title, domain, status, owner, date, WS, source-docs)
  and `_register/traceability-matrix.md` (ADR↔WS↔doc§↔requirement ID↔build phase↔code path),
  generated from YAML front matter; `_register/open-decisions.md` lists Proposed ADRs
  (ADR-D0-04).
- CI checks: every `related_adrs`/`supersedes` path resolves; every `source_docs` path exists
  under `MD files/`; each requirement (ADR-D1-12 scheme) maps to ≥1 ADR; status audit (exactly
  the Proposed set). Bidirectional upstream/downstream links per ADR §19.

## 9. Consequences

### 9.1 Positive
- Complete, current, navigable, coverage-provable decision traceability.
### 9.2 Negative
- Generation + CI-check tooling.
### 9.3 Neutral
- Anchors RAID (D8-06) and compliance mapping (D6-18).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Manual simplicity | Sync + integrity + coverage | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Governance artefact |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Registers versioned; generated from versioned ADRs |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Register drifts from ADRs | Low | Med | M | Auto-generation + CI checks (E) | Principal Architect | Low |
| RSK-02 | Broken cross-links | Med | Low | L | CI link validation | Programme Manager | Low |
| RSK-03 | Requirement uncovered | Low | Med | M | Coverage check | AI Governance Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | ADRs in register | 100% | < 100% | Register gen | Per ADR change |
| QM-02 | Broken cross-links | 0 | > 0 | CI | Per build |
| QM-03 | Requirements mapped to ≥1 ADR | 100% | < 100% | Coverage check | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Internal |
| Personal data / PII | None |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Traceability is audit evidence (ADR-D6-18) |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 21 |
| Repository paths | `docs/architecture/adr/_register/` |
| Configuration | Generation + CI checks |
| Contracts / schemas | ADR front-matter schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D0-01, D0-02, D1-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Register + matrix generated from front matter | Build check |
| AC-02 | Cross-links resolve | CI link check |
| AC-03 | Requirements covered | Coverage check |
| AC-04 | Status audit matches Proposed set | Status check |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Register/matrix CI status |
| Alerting | Broken links; coverage gaps |
| Runbook | `docs/runbooks/adr-registers.md` |
| Failure mode and degradation | CI fails on integrity break |
| Rollback | N/A |
| Support model impact | Architecture governance |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Generation + CI checks | S–M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Register scale unmanageable | Ops | Consider GRC tool (Option D) |
| RT-02 | Coverage gaps recur | QM-03 | Strengthen checks |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-36 |
| Specification sections | 20.PF-FT-AI-GOVERNANCE.md §29, §115–§116 |
| Requirement IDs | TRACE-* |
| Build phases | 21 |
| Code paths | `_register/` |
| Configuration | generation/CI |
| Tests | register CI checks |
| Upstream ADRs | ADR-D0-01, D0-02, D1-12 |
| Downstream ADRs | ADR-D8-06, D6-18 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
