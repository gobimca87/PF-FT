---
id: ADR-D5-14
title: Environment model — DEV → TEST → UAT → STAGE → PROD
domain: 5 Technology
ws_ref: [WS-24]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Platform Engineer, Release Manager, SRE]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-06, ADR-D5-12, ADR-D5-13, ADR-D7-10, ADR-D6-15]
source_docs:
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33, §34, §35, §36, §37, §38, §39, §40, §41"
  - "MD files/4 AI/17.PF-FT-AI-CONFIGURATION-VERSIONING.md §13, §16"
build_phases: [1]
impacted_paths:
  - config/
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-14 — Environment model — DEV → TEST → UAT → STAGE → PROD

## 1. Summary

PFF AI will use a **five-stage environment model — DEV → TEST → UAT → STAGE → PROD** —
with strict isolation, per-environment configuration overlays and release-manifest
promotion, so changes flow through progressively production-like stages before reaching
users (25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33–§41; 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §13). Each environment is isolated (network, data,
identity); promotion is by the immutable release manifest (ADR-D5-06).

## 2. Context and Problem Statement

25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33–§38 define the five environments, §39 environment isolation, §40–§41
configuration; 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §13/§16 environment configuration and isolation. CLAUDE.md/
DEVELOPMENT-GUIDE reference a 5-stage model. Without a defined ladder, changes reach
production under-tested, environments leak data/config into each other, and "what's in
UAT vs STAGE" is ambiguous. This ADR fixes the environment topology and promotion.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Progressive stages to production | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33–§38 |
| DR-F-02 | Strict env isolation (net/data/identity) | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §39; 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §16 |
| DR-F-03 | Per-env config overlays | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §40; ADR-D5-06 |
| DR-C-01 | Promotion via release manifest | ADR-D5-06; ADR-D7-10 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Five stages justified by risk/compliance | Collapse stages | Risk review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Risk reduction before prod | 28 | Catch issues early | Escaped-defect rate |
| EC-02 | Isolation (no cross-env leakage) | 24 | Security/compliance | Isolation tests |
| EC-03 | Promotion integrity | 18 | What-tested = what-shipped | Manifest promotion |
| EC-04 | Cost/overhead of environments | 16 | 5 envs cost | £/env |
| EC-05 | Simplicity/velocity | 14 | Not too many gates | Lead time |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Five stages DEV→TEST→UAT→STAGE→PROD, isolated, manifest-promoted

**Description.** The spec's five-stage ladder; each isolated; overlays per env; promote
the same manifest/image digest up the chain.
**Strengths.** Strong risk reduction; UAT for business sign-off; STAGE as prod-mirror;
integrity via manifest.
**Weaknesses.** Five environments to run/fund.
**Cost / effort.** Higher infra cost; strong assurance.

### 5.2 Option B — Three stages (DEV→STAGE→PROD)

**Description.** Collapse TEST/UAT into STAGE.
**Strengths.** Cheaper; faster.
**Weaknesses.** No dedicated business UAT; less isolation of automated vs acceptance
testing; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md specifies five.
**Cost / effort.** Lower; weaker assurance.

### 5.3 Option C — Two stages (DEV→PROD)

**Description.** Dev then prod.
**Strengths.** Fastest/cheapest.
**Weaknesses.** High escape risk; no UAT/stage; unacceptable for enterprise/safeguarding.
**Cost / effort.** Low; risky.

### 5.4 Option D — Ephemeral per-PR environments + prod

**Description.** Spin up throwaway envs per PR, plus prod.
**Strengths.** Great isolation for testing; parallel.
**Weaknesses.** No stable UAT/STAGE for business sign-off/perf; ephemeral infra
complexity; doesn't replace the ladder. A complement to DEV/TEST.
**Cost / effort.** Medium; complements A.

### 5.5 Option E — Six+ stages (add PERF/PENTEST env)

**Description.** Add dedicated performance/security environments.
**Strengths.** Thorough.
**Weaknesses.** More cost/overhead; perf/security testing can run in STAGE windows now.
**Cost / effort.** High.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Single shared environment | No isolation; unacceptable |
| Prod testing only | Unacceptable risk |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33–§41 and 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §13/§16.

| Criterion | Weight | A: 5-stage | B: 3-stage | C: 2-stage | D: Ephemeral+prod | E: 6+ stage |
|---|---|---|---|---|---|---|
| EC-01 Risk reduction | 28 | 5 | 4 | 2 | 4 | 5 |
| EC-02 Isolation | 24 | 5 | 4 | 2 | 5 | 5 |
| EC-03 Promotion integrity | 18 | 5 | 4 | 3 | 3 | 5 |
| EC-04 Cost | 16 | 3 | 4 | 5 | 3 | 2 |
| EC-05 Simplicity/velocity | 14 | 3 | 4 | 5 | 3 | 2 |
| **Weighted total** | **100** | **440** | **400** | **306** | **388** | **410** |

Totals (×20): **A = 440**, **E = 410**, **B = 400**, **D = 388**, **C = 306**.

**Sensitivity.** A leads; E adds cost for marginal gain (perf/security run in STAGE). B
(3-stage) is the fallback if cost pressure is high, accepting less business-UAT
isolation. Ephemeral per-PR envs (D) are adopted as a *complement* for DEV/TEST, not a
replacement.

## 7. Decision

**PFF AI will use the five-stage environment model DEV → TEST → UAT → STAGE → PROD,
each strictly isolated, configured by per-environment overlays, and promoted by the
immutable release manifest and image digest (Option A);** ephemeral per-PR
environments (D) may complement DEV/TEST. Fewer stages (B/C) are rejected for
enterprise/safeguarding risk; six+ (E) is unnecessary now.

**Status rationale.** `Accepted` — 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33–§38 define the five stages.

## 8. Architecture Detail

- Environments: DEV (integration), TEST (automated QA), UAT (business sign-off), STAGE
  (prod-mirror/perf/security window), PROD (25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §34–§38).
- Isolation (§39): separate networks, data, identities, namespaces; no shared secrets.
- Config overlays per env (§40; ADR-D5-06); promotion applies the same manifest/digest
  up the chain via CD (ADR-D7-10) with governance gates (ADR-D6-15).

## 9. Consequences

### 9.1 Positive
- Progressive assurance; business UAT; prod-mirror staging; integrity of promotion.
### 9.2 Negative
- Five environments cost more to run.
### 9.3 Neutral
- Frames CD (D7-10) and governance gates (D6-15).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Lower infra cost of fewer envs | Risk reduction + business UAT | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Env model; no business authority |
| Precedence chain | N/A |
| Four-state separation | Env isolation complements state separation |
| Versioned artefacts | Same manifest/digest promoted across envs |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Cross-env data/config leakage | Low | High | M | Strict isolation + tests (§39) | Security Architect | Low |
| RSK-02 | Env cost overrun | Med | Med | M | Right-size lower envs; ephemeral for DEV/TEST | FinOps | Low |
| RSK-03 | Drift between STAGE and PROD | Med | Med | M | Same manifest/IaC; drift detection | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Defects escaping to PROD | minimal | rising | Incident tracking | Monthly |
| QM-02 | Same digest promoted DEV→PROD | 100% | < 100% | CD audit | Per release |
| QM-03 | Cross-env isolation tests | 100% | < 100% | CI | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Isolation limits blast radius |
| Data classification touched | Non-prod uses masked/synthetic data (ADR-D4-07) |
| Personal data / PII | Real PII only in controlled envs |
| Children's data and safeguarding | Non-prod avoids real safeguarding data |
| UK GDPR lawful basis and rights impact | Data minimisation in lower envs |
| Audit and evidential requirements | Promotion + gate logs |
| Standards touched | ISO/IEC 27001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `config/<env>/`, `infra/` |
| Configuration | Per-env overlays |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-06, D5-12, D5-13, D7-10 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Five isolated environments exist | Infra audit |
| AC-02 | Same manifest/digest promoted | CD audit |
| AC-03 | Non-prod uses masked/synthetic data | Data review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Per-env health; promotion status |
| Alerting | Promotion failure; env drift |
| Runbook | `docs/runbooks/environments.md` |
| Failure mode and degradation | Failed stage blocks promotion |
| Rollback | Re-promote previous manifest |
| Support model impact | Platform + release mgmt |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| 5 environments | setup | per-env infra | Right-sized lower envs |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Cost pressure | FinOps | Collapse to 3-stage (Option B) |
| RT-02 | Dedicated perf/security env needed | Ops | Add environment (Option E) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 |
| Specification sections | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §33–§41; 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §13, §16 |
| Requirement IDs | ENV-* |
| Build phases | 1 |
| Code paths | `config/`, `infra/` |
| Configuration | per-env overlays |
| Tests | isolation + promotion tests |
| Upstream ADRs | ADR-D5-06 |
| Downstream ADRs | ADR-D7-10, D6-15 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
