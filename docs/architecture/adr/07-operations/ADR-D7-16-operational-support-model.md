---
id: ADR-D7-16
title: Operational support model, runbook ownership and service tiers
domain: 7 Operations
ws_ref: [WS-33]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Platform Engineer, AI Architecture Lead, Product Owner]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-08, ADR-D7-17, ADR-D7-18, ADR-D6-17, ADR-D7-07]
source_docs:
  - "MD files/6 Production/28.PF-FT-AI-OPERATIONS-RUNBOOK.md §2, §3, §4, §7, §16, §17, §29, §30, §161"
build_phases: [10]
impacted_paths:
  - docs/runbooks/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-16 — Operational support model, runbook ownership and service tiers

## 1. Summary

PFF AI will run a **tiered support model with clear operational boundaries, owned runbooks
and an on-call rota** — the AI platform team operates the AI layer within defined
boundaries; PFF/enterprise owns business systems; every operational procedure has a
maintained runbook and an owner (28.PF-FT-AI-OPERATIONS-RUNBOOK.md §2–§4, §7, §16–§17, §29–§30, §161). Support tiers
and escalation are explicit.

## 2. Context and Problem Statement

28.PF-FT-AI-OPERATIONS-RUNBOOK.md §2–§4 operational principle/boundaries/responsibilities, §7 production access, §16
operational golden path, §17 startup, §29–§30 health verification, §161 operational
runbook. Without a defined support model, ownership is ambiguous, runbooks rot, and
incidents stall on "who handles this". This ADR fixes the support model, runbook ownership
and service tiers.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Clear operational boundaries (AI vs enterprise) | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §3 |
| DR-F-02 | Owned, maintained runbooks | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §161 |
| DR-F-03 | Tiered support + on-call | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §4 |
| DR-C-01 | Controlled production access | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §7 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Team can staff on-call | Managed/shared on-call | Ops planning |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Clear ownership/boundaries | 28 | No stalls | Boundary clarity |
| EC-02 | Runbook coverage/quality | 24 | Fast resolution | Coverage |
| EC-03 | Response capability (on-call/tiers) | 20 | MTTR | Coverage hours |
| EC-04 | Access control | 16 | Security | Prod access model |
| EC-05 | Sustainability | 12 | Avoid burnout | On-call load |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Tiered support (L1→L3) + owned runbooks + on-call rota + controlled prod access

**Description.** Defined tiers (triage→platform→engineering), each AI-platform procedure
with an owned runbook (28.PF-FT-AI-OPERATIONS-RUNBOOK.md §161), an on-call rota with escalation (ADR-D7-08), and
controlled/audited production access (28.PF-FT-AI-OPERATIONS-RUNBOOK.md §7); boundaries with PFF explicit (§3).
**Strengths.** Clear, resolvable, secure, sustainable.
**Weaknesses.** Staffing/runbook upkeep.
**Cost / effort.** Medium.

### 5.2 Option B — Single on-call, no tiers/runbooks

**Description.** One engineer on call, ad hoc.
**Strengths.** Simple.
**Weaknesses.** Burnout; no triage; slow without runbooks.
**Cost / effort.** Low; fragile.

### 5.3 Option C — Fully outsourced/managed ops

**Description.** Third-party runs ops.
**Strengths.** Offloads ops.
**Weaknesses.** AI-specific knowledge gaps; boundary with PFF unclear; data-access concerns.
**Cost / effort.** Medium; knowledge gaps.

### 5.4 Option D — Dev-team-owns-ops (no dedicated SRE)

**Description.** Developers operate their code (you-build-it-you-run-it).
**Strengths.** Ownership; fast fixes.
**Weaknesses.** Without runbooks/tiers, inconsistent; on-call load on devs.
**Cost / effort.** Low-medium; needs structure.

### 5.5 Option E — Tiered + owned runbooks + on-call + SRE-with-dev-escalation (hybrid)

**Description.** Option A with SRE/platform on L1–L2 and dev-team escalation for L3
(deep code issues), you-build-it-you-run-it for the escalation tier.
**Strengths.** A's structure + dev ownership of deep issues.
**Weaknesses.** Coordination.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No runbooks | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §161 |
| Uncontrolled prod access | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §7 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §2–§4/§7/§16–§17/§161.

| Criterion | Weight | A: Tiered | B: Single on-call | C: Outsourced | D: Dev-owns | E: Tiered+dev-escalation |
|---|---|---|---|---|---|---|
| EC-01 Ownership | 28 | 5 | 2 | 2 | 4 | 5 |
| EC-02 Runbooks | 24 | 5 | 2 | 3 | 3 | 5 |
| EC-03 Response | 20 | 5 | 3 | 4 | 3 | 5 |
| EC-04 Access control | 16 | 5 | 3 | 2 | 4 | 5 |
| EC-05 Sustainability | 12 | 4 | 1 | 4 | 3 | 4 |
| **Weighted total** | **100** | **488** | **228** | **288** | **344** | **496** |

Totals (×20): **E = 496**, **A = 488**, **D = 344**, **C = 288**, **B = 228**.

**Sensitivity.** E (tiered + dev-team escalation for deep issues) edges A by pairing SRE
structure with developer ownership of code-level problems. Adopted. Single on-call (B) is
unsustainable; outsourcing (C) has AI-knowledge gaps.

## 7. Decision

**PFF AI will run a tiered support model (L1 triage → L2 platform/SRE → L3 dev-team
escalation) with owned, maintained runbooks, an on-call rota with escalation, and
controlled/audited production access, within explicit operational boundaries with PFF
(Option E).** Single on-call (B), full outsourcing (C) and unstructured dev-owns (D) are
rejected.

## 8. Architecture Detail

- Operational boundaries (28.PF-FT-AI-OPERATIONS-RUNBOOK.md §3): AI-platform team operates the AI layer; PFF owns
  business systems; hand-offs defined. Runbooks in `docs/runbooks/` (one per procedure,
  §161) with named owners; golden path (§16), startup (§17), health checks (§29–§39).
- On-call rota + escalation tied to severity (ADR-D7-08); production access is
  least-privilege, time-bound and audited (28.PF-FT-AI-OPERATIONS-RUNBOOK.md §7; ADR-D6-17). L3 escalation follows
  you-build-it-you-run-it for code issues.

## 9. Consequences

### 9.1 Positive
- Clear ownership, fast resolution, secure access, sustainable on-call.
### 9.2 Negative
- Staffing + runbook maintenance.
### 9.3 Neutral
- Feeds incident (D7-17) and DR (D7-18).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of single on-call | Sustainable, structured support | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Ops boundaries keep PFF owning business systems |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Runbooks versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Runbooks rot | Med | Med | M | Owner per runbook; review cadence | SRE | Low |
| RSK-02 | On-call burnout | Med | Med | M | Tiers + rotation + sustainable load | SRE | Low |
| RSK-03 | Uncontrolled prod access | Low | High | M | Least-privilege, time-bound, audited (§7) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Procedures with owned runbooks | 100% | < 100% | Runbook audit | Quarterly |
| QM-02 | MTTR by severity | within target | rising | Incident data | Monthly |
| QM-03 | Prod access audited | 100% | < 100% | Access audit | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Controlled prod access reduces risk |
| Data classification touched | Ops may touch Confidential data under control |
| Personal data / PII | Access least-privilege + audited |
| Children's data and safeguarding | Safeguarding-data access strictly controlled |
| UK GDPR lawful basis and rights impact | Access accountability |
| Audit and evidential requirements | Access + actions audited (ADR-D6-17) |
| Standards touched | ISO/IEC 27001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `docs/runbooks/` |
| Configuration | On-call rota; access policy |
| Contracts / schemas | Runbook template |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-08, D7-17, D7-18, D6-17 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Every procedure has an owned runbook | Runbook audit |
| AC-02 | On-call rota + escalation defined | Ops config |
| AC-03 | Prod access least-privilege + audited | Access audit |
| AC-04 | Boundaries with PFF documented | Doc review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | On-call load; runbook freshness; MTTR |
| Alerting | Via ADR-D7-08 |
| Runbook | `docs/runbooks/` (index) |
| Failure mode and degradation | Escalation path if L1/L2 can't resolve |
| Rollback | N/A |
| Support model impact | This ADR defines it |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| On-call + tooling | setup | staffing | Ops budget |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | MTTR rising | QM-02 | Improve runbooks/tiers |
| RT-02 | On-call overload | QM/feedback | Rebalance rota |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-33 Operations |
| Specification sections | 28.PF-FT-AI-OPERATIONS-RUNBOOK.md §2–§4, §7, §16–§17, §29–§30, §161 |
| Requirement IDs | OPS-SUP-* |
| Build phases | 10 |
| Code paths | `docs/runbooks/` |
| Configuration | on-call/access |
| Tests | runbook drills |
| Upstream ADRs | ADR-D7-08 |
| Downstream ADRs | ADR-D7-17, D7-18 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
