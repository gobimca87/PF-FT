---
id: ADR-D8-06
title: RAID register and ownership
domain: 8 Business Value
ws_ref: [WS-36]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Programme Manager
contributors: [Principal Architect, AI Governance Lead]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D0-04, ADR-D6-15, ADR-D8-07, ADR-D6-13, ADR-D7-17]
source_docs:
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §18, §19, §20, §101"
build_phases: [21]
impacted_paths:
  - docs/architecture/adr/_register/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-06 — RAID register and ownership

## 1. Summary

PFF AI will maintain a **RAID register (Risks, Assumptions, Issues, Dependencies)** with an
owner and status per entry, integrated with the existing risk register (20.PF-FT-AI-GOVERNANCE.md §18–§20),
open-decisions register (ADR-D0-04), governance exceptions (20.PF-FT-AI-GOVERNANCE.md §101) and per-ADR risk
sections — so programme-level RAID is tracked in one place and reviewed on a cadence.

## 2. Context and Problem Statement

20.PF-FT-AI-GOVERNANCE.md §18–§20 AI risk register/treatment/residual, §101 governance exceptions. ADRs each
carry risks (§11) and assumptions (§3.4); open decisions live in ADR-D0-04. Without a
consolidated RAID register, cross-cutting risks/assumptions/issues/dependencies fall through
the cracks. This ADR fixes the RAID register and its ownership.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Track R/A/I/D with owner + status | 20.PF-FT-AI-GOVERNANCE.md §18–§20 |
| DR-F-02 | Integrate with risk/open-decision/exception registers | 20.PF-FT-AI-GOVERNANCE.md §18, §101; ADR-D0-04 |
| DR-F-03 | Reviewed on a cadence | governance |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | RAID kept current by owners | Automated reminders | Review cadence |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Coverage (R/A/I/D) | 26 | Nothing lost | Categories tracked |
| EC-02 | Ownership/accountability | 24 | Action | Owner per entry |
| EC-03 | Integration (no duplication) | 20 | Single source | Register links |
| EC-04 | Reviewability | 16 | Kept current | Cadence |
| EC-05 | Simplicity | 14 | Usable | Overhead |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Consolidated RAID register integrated with existing registers, owned, reviewed

**Description.** A RAID register in `_register/` linking to the risk register (20.PF-FT-AI-GOVERNANCE.md §18),
open decisions (ADR-D0-04) and exceptions (§101); each entry has an owner + status; reviewed
on a cadence (20.PF-FT-AI-GOVERNANCE.md §90).
**Strengths.** Complete, accountable, integrated, current.
**Weaknesses.** Upkeep discipline.
**Cost / effort.** Low.

### 5.2 Option B — Risk register only (no A/I/D)

**Description.** Track risks only.
**Strengths.** Simpler.
**Weaknesses.** Assumptions/issues/dependencies untracked.
**Cost / effort.** Low; gaps.

### 5.3 Option C — RAID scattered across ADRs (no consolidation)

**Description.** Rely on per-ADR sections only.
**Strengths.** No extra artefact.
**Weaknesses.** No cross-cutting view; hard to review holistically.
**Cost / effort.** Low; fragmented.

### 5.4 Option D — External PM tool for RAID (Jira/etc.)

**Description.** RAID in a project tool.
**Strengths.** Workflow features.
**Weaknesses.** Split from the in-repo decision registers; sync overhead.
**Cost / effort.** Medium.

### 5.5 Option E — Consolidated RAID + automated linkage from ADR risk/assumption sections + review cadence

**Description.** Option A with tooling that aggregates ADR §3.4/§11 entries into the RAID
register automatically, reducing manual duplication.
**Strengths.** A + reduced manual effort + always in sync with ADRs.
**Weaknesses.** Aggregation tooling.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No RAID tracking | 20.PF-FT-AI-GOVERNANCE.md §18 |
| Duplicate risk data across tools | Sync errors |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PF-FT-AI-GOVERNANCE.md §18–§20/§90/§101 and the ADR
registers.

| Criterion | Weight | A: Consolidated | B: Risk-only | C: Scattered | D: PM tool | E: A+auto-linkage |
|---|---|---|---|---|---|---|
| EC-01 Coverage | 26 | 5 | 2 | 3 | 5 | 5 |
| EC-02 Ownership | 24 | 5 | 4 | 2 | 5 | 5 |
| EC-03 Integration | 20 | 5 | 3 | 4 | 2 | 5 |
| EC-04 Reviewability | 16 | 4 | 4 | 2 | 4 | 5 |
| EC-05 Simplicity | 14 | 4 | 5 | 4 | 3 | 4 |
| **Weighted total** | **100** | **472** | **344** | **296** | **404** | **492** |

Totals (×20): **E = 492**, **A = 472**, **D = 404**, **B = 344**, **C = 296**.

**Sensitivity.** E (A + automated aggregation from ADR sections) edges A by keeping the RAID
register in sync with ADR risks/assumptions without manual re-entry. Adopted. Risk-only (B)
and scattered (C) leave gaps.

## 7. Decision

**PFF AI will maintain a consolidated RAID register in `_register/`, integrated with the
risk register, open-decisions register (ADR-D0-04) and governance exceptions, with an owner
and status per entry, reviewed on a cadence, and automatically aggregating ADR risk/
assumption entries (Option E).** Risk-only (B), scattered (C) and external-PM-only (D) are
rejected.

## 8. Architecture Detail

- `_register/raid-register.md` (or generated) with columns: type (R/A/I/D), description,
  owner, status, severity/likelihood (risks), mitigation/action, links to source ADR/register.
- Integrates: risks from ADR §11 + 20.PF-FT-AI-GOVERNANCE.md §18; assumptions from ADR §3.4; open decisions
  (ADR-D0-04); exceptions (20.PF-FT-AI-GOVERNANCE.md §101, e.g. GOV-EX-ADR-001 from ADR-D0-01); issues from
  incidents (ADR-D7-17). Reviewed at governance cadence (20.PF-FT-AI-GOVERNANCE.md §90).

## 9. Consequences

### 9.1 Positive
- Single, owned, current view of programme RAID; nothing falls through.
### 9.2 Negative
- Aggregation tooling + review discipline.
### 9.3 Neutral
- Complements decision register (D8-07).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of risk-only | Full RAID coverage | Programme Manager |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Programme governance artefact |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | RAID register versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | RAID goes stale | Med | Med | M | Cadence review + auto-aggregation (E) | Programme Manager | Low |
| RSK-02 | Duplication with other registers | Low | Low | L | Links, not copies | Programme Manager | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | RAID entries with owner + status | 100% | < 100% | Register audit | Monthly |
| QM-02 | Overdue RAID reviews | 0 | > 0 | Governance | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Internal |
| Personal data / PII | None |
| Children's data and safeguarding | Safeguarding risks tracked here |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | RAID history retained |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 21 |
| Repository paths | `docs/architecture/adr/_register/raid-register.md` |
| Configuration | Aggregation tooling |
| Contracts / schemas | RAID entry schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D0-04, D6-15, D8-07 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | R/A/I/D all tracked | Register review |
| AC-02 | Every entry owned + status | Register audit |
| AC-03 | Linked to source registers | Link check |
| AC-04 | Reviewed on cadence | Governance record |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | RAID freshness |
| Alerting | Overdue reviews |
| Runbook | `docs/runbooks/raid.md` |
| Failure mode and degradation | Stale entry flagged |
| Rollback | N/A |
| Support model impact | Programme management |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| RAID register + aggregation | S | periodic | Governance effort |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | RAID chronically stale | QM-02 | Improve tooling/cadence |
| RT-02 | Major new risk class | Review | Extend register |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-36 RAID/Registers |
| Specification sections | 20.PF-FT-AI-GOVERNANCE.md §18–§20, §90, §101 |
| Requirement IDs | RAID-* |
| Build phases | 21 |
| Code paths | `_register/raid-register.md` |
| Configuration | aggregation |
| Tests | register audit |
| Upstream ADRs | ADR-D0-04 |
| Downstream ADRs | ADR-D8-07 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Programme Manager | Initial decision recorded. |
