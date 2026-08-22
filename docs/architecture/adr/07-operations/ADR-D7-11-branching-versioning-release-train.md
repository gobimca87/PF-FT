---
id: ADR-D7-11
title: Branching, versioning and release-train model
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Release Manager
contributors: [Backend Lead, SRE]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-09, ADR-D7-10, ADR-D5-06, ADR-D3-11, ADR-D6-15]
source_docs:
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §65, §66, §67, §68"
  - "MD files/4 AI/17.PF-FT-AI-CONFIGURATION-VERSIONING.md §58, §60"
build_phases: [0]
impacted_paths:
  - .github/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-11 — Branching, versioning and release-train model

## 1. Summary

PFF AI will use **trunk-based development with short-lived feature branches, protected
main, semantic versioning of releases, and a regular release train** that bundles code +
AI artefacts into an immutable release (ADR-D5-06) (doc 25 §65–§68; doc 17 §58, §60).
Main is always releasable; releases are versioned, dated and traceable to a git commit.

## 2. Context and Problem Statement

Doc 25 §65–§68 CI/CD/PR-gate; doc 17 §58 release manifest, §60 release id. Long-lived
branches cause merge hell and drift; ad-hoc releases lack traceability. This ADR fixes the
branching, versioning and release-cadence model.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Protected, always-releasable main | doc 25 §68 |
| DR-F-02 | Semantic versioned, traceable releases | doc 17 §58, §60 |
| DR-F-03 | Bundle code + AI artefacts per release | ADR-D5-06, D3-11 |
| DR-N-01 | Low merge overhead | trunk-based practice |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Team can integrate frequently | Feature flags for incomplete work | Team review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Integration health (no drift/merge hell) | 26 | Velocity/quality | Merge conflicts |
| EC-02 | Release traceability/versioning | 24 | Auditability | Version→commit |
| EC-03 | Always-releasable main | 20 | Ship anytime | Main green |
| EC-04 | Simplicity | 16 | Adoption | Model complexity |
| EC-05 | Bundle integrity (code+artefacts) | 14 | Compatible releases | Manifest bundle |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Trunk-based + short-lived branches + protected main + semver + release train

**Description.** Short-lived feature branches → PR (gates, ADR-D7-09) → protected main;
releases cut on a regular train, semver-tagged, bundling code + AI artefacts into an
immutable manifest (ADR-D5-06) with git-commit association (doc 17 §60).
**Strengths.** Healthy integration, traceable, always-releasable, simple.
**Weaknesses.** Needs feature flags for incomplete work.
**Cost / effort.** Low.

### 5.2 Option B — Gitflow (develop/release/hotfix branches)

**Description.** Classic Gitflow.
**Strengths.** Structured releases.
**Weaknesses.** Long-lived branches → drift/merge hell; heavier; slower.
**Cost / effort.** Medium.

### 5.3 Option C — Release-per-commit (continuous deployment to prod)

**Description.** Every merge to main deploys to prod.
**Strengths.** Fastest flow.
**Weaknesses.** Skips UAT/STAGE ladder (ADR-D5-14); risky for enterprise/safeguarding.
**Cost / effort.** Low; risky here.

### 5.4 Option D — Long-lived environment branches (env-per-branch)

**Description.** Branch per environment.
**Strengths.** Explicit env state in branches.
**Weaknesses.** Config-in-branches anti-pattern (config is overlays, ADR-D5-06); drift.
**Cost / effort.** Medium; anti-pattern.

### 5.5 Option E — Trunk-based + release train + feature flags for progressive delivery

**Description.** Option A plus feature flags to merge incomplete/rollout-gated work
safely and decouple deploy from release.
**Strengths.** A's benefits + safe incremental merge + progressive rollout.
**Weaknesses.** Flag lifecycle management.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No branch protection | doc 25 §68 |
| Unversioned releases | doc 17 §58, §60 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 25 §65–§68 and doc 17 §58/§60.

| Criterion | Weight | A: Trunk+train | B: Gitflow | C: Release-per-commit | D: Env branches | E: Trunk+flags |
|---|---|---|---|---|---|---|
| EC-01 Integration health | 26 | 5 | 2 | 5 | 2 | 5 |
| EC-02 Traceability | 24 | 5 | 4 | 3 | 3 | 5 |
| EC-03 Always-releasable | 20 | 5 | 3 | 5 | 3 | 5 |
| EC-04 Simplicity | 16 | 5 | 2 | 4 | 3 | 4 |
| EC-05 Bundle integrity | 14 | 5 | 4 | 3 | 3 | 5 |
| **Weighted total** | **100** | **500** | **300** | **408** | **276** | **488** |

Totals (×20): **A = 500**, **E = 488**, **C = 408**, **B = 300**, **D = 276**.

**Sensitivity.** A leads; feature flags (E) are adopted to merge incomplete work safely
and decouple deploy from release — a refinement of A. Release-per-commit (C) skips the
enterprise env ladder; Gitflow (B) and env-branches (D) cause drift.

## 7. Decision

**PFF AI will use trunk-based development with short-lived feature branches, protected
always-releasable main, semantic-versioned releases on a regular release train bundling
code + AI artefacts into an immutable manifest, with feature flags for progressive
delivery (Option E, trunk-based).** Gitflow (B), release-per-commit-to-prod (C) and
env-branches (D) are rejected.

## 8. Architecture Detail

- Branch protection on main (required checks ADR-D7-09, reviews ADR-D6-15); short-lived
  branches; squash-merge; semver tags; release train cadence.
- Each release = an immutable manifest (ADR-D5-06) pinning code image digest (ADR-D5-09)
  + AI artefact versions (prompts ADR-D3-11, models ADR-D3-15, index) with git-commit
  association (doc 17 §60); promoted via CD (ADR-D7-10) through the ladder (ADR-D5-14).
- Feature flags (governed) gate incomplete/risky features; flag cleanup tracked.

## 9. Consequences

### 9.1 Positive
- Healthy integration, traceable versioned releases, always-releasable main.
### 9.2 Negative
- Feature-flag lifecycle to manage.
### 9.3 Neutral
- Ties CI/CD/manifest/governance.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Gitflow's explicit release branches | Integration health + simplicity | Release Manager |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Engineering process; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Releases are immutable, versioned, traceable |
| Adam persona governs *how*, not *what* | Persona ships as a versioned artefact in the bundle |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Incomplete work destabilises main | Med | Med | M | Feature flags + gates | Backend Lead | Low |
| RSK-02 | Stale feature flags accrue | Med | Low | L | Flag cleanup tracking | Release Manager | Low |
| RSK-03 | Untraceable release | Low | Med | M | Manifest + git-commit id | Release Manager | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Main always green | 100% | < 100% | CI | Continuous |
| QM-02 | Releases with version→commit trace | 100% | < 100% | Release audit | Per release |
| QM-03 | Long-lived branches | ≈ 0 | rising | Repo metrics | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Branch protection prevents unreviewed changes |
| Data classification touched | Internal |
| Personal data / PII | N/A |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Release traceability |
| Standards touched | ISO 9001, ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0 |
| Repository paths | `.github/` (branch protection), release tooling |
| Configuration | Branch rules; semver; flags |
| Contracts / schemas | Release manifest (ADR-D5-06) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-09, D7-10, D5-06, D3-11 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Main protected + always green | Branch config |
| AC-02 | Releases semver-tagged + commit-traceable | Release audit |
| AC-03 | Release bundles code + AI artefacts | Manifest review |
| AC-04 | Feature flags govern incomplete work | Code review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Main health; release cadence; flag count |
| Alerting | Main broken |
| Runbook | `docs/runbooks/release.md` |
| Failure mode and degradation | Broken main blocks release train until fixed |
| Rollback | Re-release prior manifest (ADR-D7-10) |
| Support model impact | Release management |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Release tooling + flags | S | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Frequent main breakage | QM-01 | Strengthen gates/flags |
| RT-02 | Flag debt high | QM-03 | Flag-cleanup sprint |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 |
| Specification sections | doc 25 §65–§68; doc 17 §58, §60 |
| Requirement IDs | REL-* |
| Build phases | 0 |
| Code paths | `.github/`, release tooling |
| Configuration | branch rules/semver |
| Tests | release drills |
| Upstream ADRs | ADR-D7-09, D5-06 |
| Downstream ADRs | ADR-D7-10, D7-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Release Manager | Initial decision recorded. |
