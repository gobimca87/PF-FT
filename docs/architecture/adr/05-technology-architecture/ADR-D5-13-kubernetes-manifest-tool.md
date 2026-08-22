---
id: ADR-D5-13
title: Kubernetes manifest tool — Helm vs Kustomize
domain: 5 Technology
ws_ref: [WS-24]
status: Proposed
version: 1.0.0
date: 2026-08-22
decision_owner: Platform Engineer
contributors: [SRE, Backend Lead]
reviewers: [Principal Architect, Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-08, ADR-D5-12, ADR-D5-14, ADR-D7-10, ADR-D0-04]
source_docs:
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §45, §46, §47, §48, §49, §50, §67"
build_phases: [1]
impacted_paths:
  - deploy/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-13 — Kubernetes manifest tool — Helm vs Kustomize

> **OPEN DECISION** (`status: Proposed`, per ADR-D0-04 and CLAUDE.md). Full evaluation
> and a recommendation are given; final selection awaits platform-team confirmation and
> is gated at build Phase 1. Not Accepted.

## 1. Summary

PFF AI will template/customise its Kubernetes manifests with a single tool. The
**recommendation is Kustomize** (base + per-environment overlays) for its
template-free, GitOps-friendly, drift-transparent model that matches the platform's
base+overlay config philosophy (ADR-D5-06), with **Helm** as the fallback where
packaged, parameterised releases or third-party charts are needed. `Proposed` pending
platform-team confirmation.

## 2. Context and Problem Statement

Doc 25 §45–§46 define Kubernetes manifests and configuration, §47–§50 health probes,
§67 the CD pipeline; CLAUDE.md lists the manifest tool as unresolved (Helm vs
Kustomize). The tool shapes how the API, workers and (later) SLM serving are deployed
across five environments, how overlays differ, and how GitOps/CD applies them. This ADR
evaluates and recommends, pending team confirmation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Environment-specific manifest customisation | doc 25 §40, §46; ADR-D5-14 |
| DR-F-02 | Health probes + resource config expressed cleanly | doc 25 §47–§50 |
| DR-F-03 | Fits CD/GitOps apply | doc 25 §67; ADR-D7-10 |
| DR-N-01 | Matches base+overlay config philosophy | ADR-D5-06 |
| DR-F-04 | Ability to consume third-party charts | operational |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Few third-party charts needed | Helm's chart reuse gains weight | Dependency review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Env overlay clarity / drift transparency | 26 | 5-env model; GitOps | Overlay model |
| EC-02 | Simplicity / template-free readability | 20 | Fewer footguns | Templating complexity |
| EC-03 | Fit with config philosophy (base+overlay) | 16 | Consistency (D5-06) | Alignment |
| EC-04 | Third-party chart reuse | 16 | Ecosystem components | Chart availability |
| EC-05 | Release/rollback semantics | 12 | Ops | Release model |
| EC-06 | Tooling/CD integration | 10 | GitOps/CD | kubectl/Flux/Argo fit |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Kustomize (base + overlays)

**Description.** Template-free YAML with a base + per-environment overlays; native to
`kubectl`; patches/strategic-merge.
**Strengths.** No templating language; transparent diffs; GitOps-friendly; mirrors the
base+overlay config model (ADR-D5-06); no release state.
**Weaknesses.** No packaging/versioned releases; consuming third-party charts is
awkward; complex parameterisation is verbose.
**Cost / effort.** Low.

### 5.2 Option B — Helm

**Description.** Templated charts with values per environment; release history via
Tiller-less Helm 3.
**Strengths.** Packaging + versioned releases + rollback; huge chart ecosystem; strong
parameterisation.
**Weaknesses.** Go-templating complexity/footguns; rendered output less transparent;
release state to manage.
**Cost / effort.** Medium.

### 5.3 Option C — Helm + Kustomize (Helm for third-party, Kustomize for own apps)

**Description.** Use each where it shines: Helm to install third-party charts, Kustomize
for first-party manifests (post-render or separate).
**Strengths.** Best of both; common real-world pattern.
**Weaknesses.** Two tools to learn/maintain; more moving parts.
**Cost / effort.** Medium.

### 5.4 Option D — Raw manifests (kubectl apply, per-env copies)

**Description.** Hand-maintained YAML per environment.
**Strengths.** Simplest to read.
**Weaknesses.** Duplication/drift across 5 envs; error-prone; no DRY.
**Cost / effort.** Low authoring, high drift.

### 5.5 Option E — jsonnet / cdk8s (programmatic manifests)

**Description.** Generate manifests via jsonnet or cdk8s.
**Strengths.** Powerful abstraction/DRY.
**Weaknesses.** New language/toolchain; steeper curve; smaller team familiarity.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Manual portal/kubectl edits | doc 25 §45 — declarative manifests in Git |
| Config baked per-image only | No env overlay flexibility |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4 from tool characteristics and the base+overlay
config philosophy (ADR-D5-06).

| Criterion | Weight | A: Kustomize | B: Helm | C: Helm+Kustomize | D: Raw | E: jsonnet/cdk8s |
|---|---|---|---|---|---|---|
| EC-01 Overlay/drift clarity | 26 | 5 | 3 | 4 | 2 | 4 |
| EC-02 Simplicity | 20 | 5 | 3 | 3 | 4 | 2 |
| EC-03 Config-philosophy fit | 16 | 5 | 3 | 4 | 3 | 3 |
| EC-04 Third-party charts | 16 | 2 | 5 | 5 | 1 | 3 |
| EC-05 Release/rollback | 12 | 3 | 5 | 5 | 2 | 3 |
| EC-06 CD integration | 10 | 5 | 4 | 4 | 3 | 4 |
| **Weighted total** | **100** | **432** | **376** | **420** | **246** | **314** |

Totals (×20): **A = 432**, **C = 420**, **B = 376**, **E = 314**, **D = 246**.

**Sensitivity.** Kustomize (A) narrowly leads the hybrid (C, 420). **The deciding
factor is third-party chart need (EC-04): if the platform pulls in several Helm charts
(e.g. an ingress controller, Langfuse, GPU operator), the hybrid (C) becomes the
pragmatic winner** — which is why this is `Proposed`. For first-party apps alone,
Kustomize's transparency wins.

## 7. Decision

**Recommendation: Kustomize (base + per-environment overlays) for first-party
manifests, with Helm as the fallback/complement for third-party charts (hybrid,
Option C, if chart consumption grows).** This mirrors the base+overlay config model
(ADR-D5-06) and keeps diffs transparent for GitOps/CD (ADR-D7-10). Raw manifests (D)
and jsonnet/cdk8s (E) are not pursued. Confirmed by the platform team before Phase 1.

**Status rationale.** `Proposed` per ADR-D0-04/CLAUDE.md — an open decision; carries a
recommendation with a clear trigger (third-party chart need) for adopting the hybrid.
Listed in `_register/open-decisions.md`. Not Accepted.

## 8. Architecture Detail

- `deploy/base/` + `deploy/overlays/<env>/` (Kustomize); manifests express Deployments,
  Services, HPAs, health probes (doc 25 §47–§50), resource requests/limits (§19).
- CD (ADR-D7-10) renders + applies the overlay for the target environment; GitOps
  (Argo/Flux) optional.
- Where a third-party chart is needed, Helm installs it (Option C); first-party stays
  Kustomize.
- Image digests (ADR-D5-09) and config/manifest versions (ADR-D5-06) drive deployments.

## 9. Consequences

### 9.1 Positive
- Transparent, DRY, GitOps-friendly manifests aligned to the config model.
### 9.2 Negative
- Kustomize alone is weak on third-party charts (hence hybrid trigger).
### 9.3 Neutral
- Pairs with IaC (D5-12) and env model (D5-14).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Helm's packaging/versioned releases | Transparency + config-model fit | Platform Eng |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Deployment tooling; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Manifests versioned in Git; images by digest |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Third-party chart need grows, Kustomize awkward | Med | Med | M | Adopt hybrid (Option C) | Platform Eng | Low |
| RSK-02 | Overlay drift across envs | Low | Med | M | Base+overlay + CD render checks | SRE | Low |
| RSK-03 | Rollback less clean than Helm | Low | Med | M | Git revert + redeploy; image digests | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Deploys via managed manifests | 100% | < 100% | CD | Per deploy |
| QM-02 | Env overlay drift | ≈ 0 | rising | Render diff | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Declarative, reviewed manifests |
| Data classification touched | Internal |
| Personal data / PII | None in manifests (secrets by ref, ADR-D5-07) |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Git history + CD logs |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `deploy/` |
| Configuration | base + overlays; probes; HPAs |
| Contracts / schemas | K8s manifests |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-08, D5-12, D5-14, D7-10 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Single manifest approach for first-party apps | Repo review |
| AC-02 | Per-env overlays render correctly | CD render test |
| AC-03 | Health probes present on all deployments | Manifest lint |
| AC-04 | Secrets by reference, none inline | Manifest scan |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Deployment status; rollout health |
| Alerting | Failed rollout |
| Runbook | `docs/runbooks/deploy.md` |
| Failure mode and degradation | Rolling update with probes; auto-rollback on failure |
| Rollback | Git revert + redeploy previous digest |
| Support model impact | Platform + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Tooling | none (OSS) | none | Kustomize/Helm OSS |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Multiple third-party charts required | Dependency review | Adopt hybrid Helm+Kustomize (Option C) |
| RT-02 | Overlay complexity unmanageable | Ops | Evaluate cdk8s/jsonnet (Option E) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 |
| Specification sections | doc 25 §45–§50, §67 |
| Requirement IDs | INFRA-K8S-* |
| Build phases | 1 |
| Code paths | `deploy/` |
| Configuration | base/overlays |
| Tests | render + lint tests |
| Upstream ADRs | ADR-D5-08, D5-12, D0-04 |
| Downstream ADRs | ADR-D5-14, D7-10 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Platform Engineer | Initial decision recorded — OPEN (Proposed); recommend Kustomize, hybrid with Helm as fallback. |
