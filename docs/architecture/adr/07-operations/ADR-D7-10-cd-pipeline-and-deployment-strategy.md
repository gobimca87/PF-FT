---
id: ADR-D7-10
title: CD pipeline and deployment strategy — rolling updates
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.1.0
date: 2026-08-22
decision_owner: SRE
contributors: [Platform Engineer, Release Manager]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-14, ADR-D5-13, ADR-D5-20, ADR-D5-06, ADR-D7-09, ADR-D6-15]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §67, §47, §48, §49, §50"
  - "MD files/6 Production/28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23, §40, §41, §42, §43"
build_phases: [1]
impacted_paths:
  - .github/workflows/
  - deploy/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-10 — CD pipeline and deployment strategy — rolling updates

> **Amendment (v1.1.0, 2026-09-05) — realizing toolchain.** Per **ADR-D5-20**, CD is
> executed by the enterprise **Azure DevOps `release.yaml`** pipeline promoting the
> immutable image/manifest through the environment ladder onto the shared enterprise **AKS**
> platform, using the enterprise deployment model and the same platform team. **The
> decision is unchanged** — rolling-default with health probes and post-deploy smoke tests,
> canary/blue-green where specified, and fast rollback to the previous digest all still
> apply; only the executing toolchain is named. Read "`.github/workflows/`" below as "the
> enterprise Azure DevOps `release.yaml`".

## 1. Summary

PFF AI will deploy via a **CD pipeline promoting an immutable release manifest/image
digest through the environment ladder (ADR-D5-14)** using **rolling updates with health
probes and automated post-deployment smoke tests**, with fast rollback to the previous
digest (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §47–§50, §67; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23, §40–§43). AI artefacts (prompts/models/index)
promote through the same manifest (ADR-D5-06) under change governance (ADR-D6-15).

## 2. Context and Problem Statement

25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §67 CD pipeline, §47–§50 health/liveness/readiness/startup probes; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23
post-deployment smoke test, §40–§43 deployment/version validation and rollback. Without a
defined deployment strategy, releases risk downtime, bad versions and slow recovery. This
ADR fixes the CD strategy (D5-14 = env ladder; D5-13 = manifests; D6-15 = gates).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Promote immutable manifest/digest through ladder | ADR-D5-06/D5-14 |
| DR-F-02 | Rolling update with health probes | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §47–§50, §67 |
| DR-F-03 | Post-deploy smoke test | 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23 |
| DR-F-04 | Fast rollback to prior digest | 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §42–§43 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Rolling suits stateless services | Blue/green for stateful/GPU | Deploy review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Zero/low-downtime deploys | 26 | Availability | Downtime |
| EC-02 | Safety (probes/smoke/rollback) | 24 | Catch bad releases | Bad-release catch |
| EC-03 | Promotion integrity (same digest) | 20 | What-tested=shipped | Digest promotion |
| EC-04 | Speed/simplicity | 16 | Velocity | Deploy time |
| EC-05 | Cost | 14 | Infra | Extra capacity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Rolling updates + health probes + smoke test + digest promotion + fast rollback

**Description.** CD promotes the manifest/digest per environment (ADR-D5-14); rolling
update with readiness/liveness/startup probes (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §47–§50); automated smoke test
post-deploy (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23); rollback to previous digest (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §42–§43).
**Strengths.** Low-downtime, safe, integrity-preserving, quick recovery.
**Weaknesses.** Rolling mixes versions briefly.
**Cost / effort.** Low-medium.

### 5.2 Option B — Blue/green deployment

**Description.** Full parallel environment, switch traffic.
**Strengths.** Instant switch/rollback; no mixed versions.
**Weaknesses.** Double capacity cost; heavier. Best reserved for GPU/index cutovers.
**Cost / effort.** Higher.

### 5.3 Option C — Canary deployment

**Description.** Route a % to the new version, ramp up.
**Strengths.** Limits blast radius; great for risky changes.
**Weaknesses.** Needs traffic-splitting + canary analysis; more setup. Valuable for model
/prompt changes.
**Cost / effort.** Medium.

### 5.4 Option D — Recreate (stop old, start new)

**Description.** Down then up.
**Strengths.** Simplest.
**Weaknesses.** Downtime; unacceptable for a conversational service.
**Cost / effort.** Low; downtime.

### 5.5 Option E — Rolling by default + canary for AI-artefact/high-risk changes + blue/green for GPU/index

**Description.** Option A as default, with canary (C) for model/prompt/high-risk changes
(shadow/canary per 15.PFF-FA-AI-SLM.md §157–§158) and blue/green (B) for GPU serving and vector-index
cutovers (ADR-D3-24/D5-10).
**Strengths.** Right strategy per change type; safe + economical.
**Weaknesses.** Multiple strategies to operate.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Manual deploys | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §67 (automated CD) |
| Mutable-tag deploys | ADR-D5-09 (digest) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §47–§50/§67 and 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md
§23/§40–§43.

| Criterion | Weight | A: Rolling | B: Blue/green | C: Canary | D: Recreate | E: Rolling+canary+B/G |
|---|---|---|---|---|---|---|
| EC-01 Downtime | 26 | 5 | 5 | 5 | 1 | 5 |
| EC-02 Safety | 24 | 4 | 5 | 5 | 2 | 5 |
| EC-03 Promotion integrity | 20 | 5 | 5 | 5 | 4 | 5 |
| EC-04 Speed/simplicity | 16 | 5 | 3 | 3 | 5 | 3 |
| EC-05 Cost | 14 | 5 | 2 | 4 | 5 | 4 |
| **Weighted total** | **100** | **472** | **424** | **456** | **300** | **464** |

Totals (×20): **A = 472**, **E = 464**, **C = 456**, **B = 424**, **D = 300**.

**Sensitivity.** A (rolling) leads for the common stateless case; E formalises using
canary for risky AI-artefact changes and blue/green for GPU/index cutovers where those
strengths matter. Adopted as **rolling-by-default with canary/blue-green per change
type**. Recreate (D) is rejected (downtime).

## 7. Decision

**PFF AI will use rolling updates with health probes and automated post-deploy smoke
tests as the default, promoting the immutable manifest/image digest through the
environment ladder with fast rollback to the previous digest; canary is used for
model/prompt/high-risk changes and blue/green for GPU serving and vector-index cutovers
(Option E, rolling-default).** Recreate (D) and manual/mutable-tag deploys are rejected.

## 8. Architecture Detail

- CD (`.github/workflows/`) promotes the release manifest (ADR-D5-06) + image digest
  (ADR-D5-09) per environment (ADR-D5-14) after gates (ADR-D7-09) and governance approval
  (ADR-D6-15); manifests applied via ADR-D5-13.
- Rolling update honours readiness/liveness/startup probes (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §47–§50); smoke test
  (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23–§24) verifies post-deploy; failure → auto-rollback to prior digest (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md
  §42–§43). Canary/shadow for models (15.PFF-FA-AI-SLM.md §157–§158); blue/green for index (14.PFF-FA-AI-EMBEDDING-VECTOR.md
  §77) and GPU serving (ADR-D5-10).

## 9. Consequences

### 9.1 Positive
- Low-downtime, safe, integrity-preserving deploys with quick recovery.
### 9.2 Negative
- Multiple strategies to operate (E).
### 9.3 Neutral
- Ties env ladder, manifest, gates, governance.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single-strategy simplicity | Right strategy per change type | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Deployment is ops; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Deploy by immutable manifest/digest |
| Adam persona governs *how*, not *what* | Persona changes deploy as canary prompt changes |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Bad release reaches prod | Low | High | M | Smoke test + auto-rollback + canary for risky | SRE | Low |
| RSK-02 | Rolling mixed-version issue | Low | Med | M | Backward-compatible changes; canary | Backend Lead | Low |
| RSK-03 | Slow rollback | Low | High | M | Prior digest retained; one-step rollback | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Deploy downtime | ~0 | > 0 | Deploy metrics | Per deploy |
| QM-02 | Bad releases caught pre-prod / auto-rolled-back | high | falling | Deploy data | Monthly |
| QM-03 | Rollback time | ≤ target | slow | Drills | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Digest deploys prevent wrong-image runs |
| Data classification touched | Internal |
| Personal data / PII | None |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Deploy records (ADR-D6-17) |
| Standards touched | ISO 9001, ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `.github/workflows/`, `deploy/` |
| Configuration | Rolling/canary/blue-green settings; probes; smoke |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-14, D5-13, D5-06, D7-09, D6-15 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Deploys promote immutable digest via ladder | CD audit |
| AC-02 | Rolling honours probes; smoke test runs | Deploy test |
| AC-03 | Auto-rollback on smoke failure | Drill |
| AC-04 | Canary used for model/prompt changes | Config |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Deploy status; rollout health; smoke results |
| Alerting | Failed rollout/smoke |
| Runbook | `docs/runbooks/deploy.md` (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §40–§47) |
| Failure mode and degradation | Rollout failure → auto-rollback |
| Rollback | Previous digest re-promoted |
| Support model impact | SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| CD + canary/blue-green infra | M | small–medium | Extra capacity for B/G/canary |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Mixed-version incidents | Post-incident | Prefer canary/blue-green |
| RT-02 | Rollback too slow | QM-03 | Improve rollback automation |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §47–§50, §67; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §23, §40–§43 |
| Requirement IDs | CD-* |
| Build phases | 1 |
| Code paths | `.github/workflows/`, `deploy/` |
| Configuration | deploy strategy |
| Tests | deploy drills |
| Upstream ADRs | ADR-D5-14, D5-06, D7-09 |
| Downstream ADRs | ADR-D6-15 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
| 1.1.0 | 2026-09-05 | SRE | Compatible amendment: CD realized on the Enterprise Application delivery model (ADR-D5-20) — enterprise Azure DevOps `release.yaml` to the shared AKS platform. Rolling-default strategy, canary/blue-green and rollback unchanged; forward-reference + related_adrs added. |
