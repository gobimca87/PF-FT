---
id: ADR-D7-09
title: CI pipeline design and mandatory quality gates
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.1.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [Platform Engineer, SRE, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-02, ADR-D5-04, ADR-D5-05, ADR-D5-20, ADR-D7-13, ADR-D7-14, ADR-D6-15]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §65, §66, §68"
  - "MD files/6 Production/27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §4, §12, §13"
build_phases: [0]
impacted_paths:
  - .github/workflows/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-09 — CI pipeline design and mandatory quality gates

> **Amendment (v1.1.0, 2026-09-05) — realizing toolchain.** Per **ADR-D5-20**, the CI
> **realization follows the Enterprise Application delivery model**: the mandatory gates
> below run in the enterprise **Azure DevOps `build.yaml`** pipeline, and code quality is
> gated by the enterprise **SonarQube Quality Gate** (Python coverage + code smells + bugs
> + vulnerabilities), rather than a standalone GitHub Actions system. **The decision is
> unchanged** — the same mandatory gates (Ruff, mypy strict, pytest, security/dependency
> scans, AI-evaluation gates), tiered execution and green-to-merge still apply; only the
> executing toolchain is named. Any repo-local GitHub Actions workflow is an interim mirror
> for PR feedback, not the authoritative pipeline. Read "`.github/workflows/`" below as "the
> enterprise Azure DevOps pipeline (with an optional repo-local mirror)".

## 1. Summary

PFF AI's CI will run **mandatory quality gates on every PR** — lint/format (Ruff,
ADR-D5-05), type check (mypy strict, ADR-D5-02), unit/component tests (ADR-D7-14),
security + dependency scans (ADR-D6-18), and AI-evaluation gates where relevant
(ADR-D7-13) — with a green pipeline required to merge (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §65–§66, §68; 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §4,
§12–§13). Gates are fast, deterministic and block merge on failure.

## 2. Context and Problem Statement

25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §65–§66 CI/CD architecture and CI pipeline, §68 PR gate; 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §4 architecture
compliance, §12–§13 lint/type-check. Without mandatory CI gates, regressions, style
drift, type errors and vulnerabilities reach main. This ADR fixes the CI pipeline and its
required gates.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Mandatory gates on every PR | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §68 |
| DR-F-02 | Lint/type/test/security/eval gates | 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §12–§13; ADR-D5-05/02, D6-18, D7-13 |
| DR-N-01 | Fast, deterministic feedback | CI practice |
| DR-C-01 | Green required to merge | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §68 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Eval gates can run in CI time | Nightly/staged eval | ADR-D7-13 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Defect/regression prevention | 30 | Core purpose | Escaped defects |
| EC-02 | Coverage of gate types | 22 | Completeness | Gates present |
| EC-03 | Speed/feedback | 20 | Dev velocity | CI duration |
| EC-04 | Determinism (no flake) | 16 | Trust | Flake rate |
| EC-05 | Maintainability | 12 | Sustainable | Pipeline complexity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Full mandatory gate set on every PR (lint/type/test/security/eval), green-to-merge

**Description.** One CI pipeline running all gates on PR; branch protection requires
green; fast unit/component tests inline, heavier eval staged if needed (ADR-D7-13).
**Strengths.** Comprehensive, blocks regressions, enforced.
**Weaknesses.** Must manage CI time.
**Cost / effort.** Medium.

### 5.2 Option B — Lint + tests only

**Description.** Basic gates.
**Strengths.** Fast, simple.
**Weaknesses.** No security/type/eval gates; misses key regressions.
**Cost / effort.** Low; gaps.

### 5.3 Option C — Nightly full checks, light PR gate

**Description.** Light PR CI; full checks nightly.
**Strengths.** Fast PRs.
**Weaknesses.** Regressions merge and are found late; not green-to-merge.
**Cost / effort.** Low; late detection.

### 5.4 Option D — Manual review only (no automated gates)

**Description.** Rely on reviewers.
**Strengths.** Human judgement.
**Weaknesses.** Inconsistent; misses mechanical checks.
**Cost / effort.** Low; unreliable.

### 5.5 Option E — Full gates on PR + tiered execution (fast inline, heavy on merge-queue/staged) + required checks

**Description.** Option A with tiered execution: fast gates inline on PR, heavier gates
(full eval, integration) on a merge queue / pre-merge stage, all required.
**Strengths.** Comprehensive + fast PR feedback + all gates enforced.
**Weaknesses.** Merge-queue setup.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No CI | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §65 |
| Optional gates | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §68 (required) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §65–§68 and 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §12–§13.

| Criterion | Weight | A: Full PR gates | B: Lint+tests | C: Nightly | D: Manual | E: Full+tiered |
|---|---|---|---|---|---|---|
| EC-01 Prevention | 30 | 5 | 3 | 2 | 2 | 5 |
| EC-02 Coverage | 22 | 5 | 2 | 4 | 1 | 5 |
| EC-03 Speed | 20 | 3 | 5 | 5 | 4 | 5 |
| EC-04 Determinism | 16 | 4 | 4 | 4 | 3 | 4 |
| EC-05 Maintainability | 12 | 4 | 5 | 3 | 4 | 3 |
| **Weighted total** | **100** | **436** | **352** | **352** | **256** | **472** |

Totals (×20): **E = 472**, **A = 436**, **B = 352**, **C = 352**, **D = 256**.

**Sensitivity.** E (full gates + tiered execution/merge queue) wins by keeping PR feedback
fast while enforcing all gates. Adopted. Lint+tests-only (B) and nightly (C) let
regressions through PRs.

## 7. Decision

**PFF AI CI will run the full mandatory gate set — Ruff lint/format, mypy strict, unit/
component tests, security + dependency scans, and AI-evaluation gates — with tiered
execution (fast gates inline on PR, heavier gates on a pre-merge/merge-queue stage), all
required and green-to-merge (Option E).** Lint+tests-only (B), nightly-only (C) and
manual (D) are rejected.

## 8. Architecture Detail

- `.github/workflows/`: PR pipeline runs Ruff (ADR-D5-05), mypy (ADR-D5-02), unit/
  component tests (ADR-D7-14), secret + dependency + SAST scans (ADR-D6-18), and
  architecture-compliance checks (import-linter, 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §4); heavier integration/eval
  gates (ADR-D7-13) run pre-merge; branch protection requires all.
- Deterministic mock SLM (ADR-D7-14) keeps AI tests stable; caching keeps CI fast.

## 9. Consequences

### 9.1 Positive
- Regressions/vulns/type errors blocked before merge; fast PR feedback.
### 9.2 Negative
- Merge-queue + CI-time management.
### 9.3 Neutral
- Feeds CD (D7-10) and change governance (D6-15).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of light CI | Comprehensive prevention | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | CI is engineering; no business authority |
| Precedence chain | Eval gates protect authoritative-truth fidelity |
| Four-state separation | Architecture checks enforce boundaries |
| Versioned artefacts | CI as code |
| Adam persona governs *how*, not *what* | Persona eval part of gates (ADR-D7-13) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Flaky tests erode trust | Med | Med | M | Deterministic mock SLM; quarantine policy (no skip in prod code) | Backend Lead | Low |
| RSK-02 | CI too slow | Med | Med | M | Tiered execution + caching (E) | Platform Eng | Low |
| RSK-03 | Gate bypass | Low | High | M | Branch protection required checks | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | PRs merged green | 100% | < 100% | CI | Per merge |
| QM-02 | PR CI duration | ≤ target | rising | CI metrics | Monthly |
| QM-03 | Flake rate | ≈ 0 | rising | CI metrics | Weekly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Security/dep scans in CI reduce risk |
| Data classification touched | Internal |
| Personal data / PII | No real PII in CI (synthetic) |
| Children's data and safeguarding | No real children's data in CI |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | CI results retained |
| Standards touched | ISO 9001, ISO/IEC 27001, NIST SSDF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0 |
| Repository paths | `.github/workflows/` |
| Configuration | Gate definitions; branch protection |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-02/04/05, D7-13/14, D6-18 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All gates run on PR/pre-merge | CI config |
| AC-02 | Green required to merge | Branch protection |
| AC-03 | Architecture checks enforced | Import-linter in CI |
| AC-04 | AI tests deterministic | Mock SLM (ADR-D7-14) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | CI pass rate, duration, flake |
| Alerting | CI outages; flake spikes |
| Runbook | `docs/runbooks/ci.md` |
| Failure mode and degradation | Gate fail → block merge |
| Rollback | Workflow revert |
| Support model impact | Platform + backend |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| CI runners | setup | CI minutes | CI pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | CI too slow | QM-02 | Optimise tiers/caching |
| RT-02 | Regression escapes CI | Post-incident | Add gate/test |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 CI/CD |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §65–§66, §68; 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §4, §12–§13 |
| Requirement IDs | CI-* |
| Build phases | 0 |
| Code paths | `.github/workflows/` |
| Configuration | gates/branch protection |
| Tests | CI itself |
| Upstream ADRs | ADR-D5-02, D5-05 |
| Downstream ADRs | ADR-D7-10, D7-13, D6-15 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
| 1.1.0 | 2026-09-05 | Backend Lead | Compatible amendment: CI realized on the Enterprise Application delivery model (ADR-D5-20) — enterprise Azure DevOps `build.yaml` + SonarQube Quality Gate rather than a standalone GitHub Actions system. Mandatory gates, tiered execution and green-to-merge unchanged; forward-reference + related_adrs added. |
