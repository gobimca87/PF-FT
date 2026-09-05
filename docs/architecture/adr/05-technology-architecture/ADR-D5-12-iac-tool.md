---
id: ADR-D5-12
title: Infrastructure-as-Code approach — conform to the Enterprise Application delivery model
domain: 5 Technology
ws_ref: [WS-24]
status: Accepted
version: 2.0.0
date: 2026-09-05
decision_owner: Platform Engineer
contributors: [SRE, Security Architect, Principal Architect]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-08, ADR-D5-13, ADR-D5-14, ADR-D5-20, ADR-D0-04]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §42, §43, §44"
build_phases: [1]
impacted_paths:
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-12 — Infrastructure-as-Code approach — conform to the Enterprise Application delivery model

> **ACCEPTED (v2.0.0).** The platform team's house-standard confirmation — the condition
> this ADR was `Proposed` pending — has been given: PFF AI **conforms to the Enterprise
> Application delivery model** rather than standing up a separate IaC toolchain of its own.
> The standalone Terraform-vs-Bicep evaluation below (§4–§6) is retained as historical
> context; the selected outcome (§7) is to adopt the enterprise standard. The binding
> cross-cutting decision is **ADR-D5-20**.

## 1. Summary

PFF AI's Azure infrastructure is defined and provisioned through the **Enterprise
Application's existing Infrastructure-as-Code and delivery model** — the same IaC
approach, Azure DevOps `build.yaml`/`release.yaml` pipelines, AKS platform, platform
team and shared resources already used by the enterprise applications (ADR-D5-20). PFF
AI does **not** select or maintain a separate, parallel IaC tool. Where the enterprise
standard is Terraform or Bicep, PFF AI uses the same; the standalone tool evaluation
below is superseded by the decision to keep infrastructure tooling **consistent with the
enterprise platform** rather than divergent. This ratifies the previously `Proposed`
recommendation into the enterprise-conformant decision on the platform team's confirmation.

## 2. Context and Problem Statement

25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §42–§44 require infrastructure-as-code with a defined structure and principles;
CLAUDE.md lists the IaC tool as unresolved (Terraform vs Bicep). The choice affects
state management, module reuse, review workflow, multi-cloud portability and team
skills across every Azure resource (AKS, APIM, KV, SB, ACR, networking). This ADR
evaluates and recommends, pending team confirmation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Declarative IaC for all Azure resources | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §42–§44 |
| DR-F-02 | Plan/preview + review before apply | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §44 |
| DR-N-01 | Module reuse across 5 environments | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §33–§38; ADR-D5-14 |
| DR-N-02 | State management + drift detection | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §44 |
| DR-C-01 | Fits team skills + org standard | organisational |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Single-cloud (Azure) for foreseeable future | Portability raises Terraform's edge | ADR-D8-10 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Azure resource coverage/fidelity | 22 | Must cover all services | Coverage/lag |
| EC-02 | Module reuse across environments | 20 | 5-env model (D5-14) | Module system |
| EC-03 | State/plan/drift workflow | 18 | Safe applies | Plan + drift |
| EC-04 | Team skills / org standard | 16 | Adoption | Familiarity |
| EC-05 | Portability / ecosystem | 14 | Avoid lock-in | Multi-cloud/providers |
| EC-06 | Operational simplicity | 10 | Run it | State/backend ops |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Terraform (with azurerm provider; OpenTofu-compatible)

**Description.** HCL modules; remote state (Azure Storage backend); `plan`/`apply`;
huge provider/module ecosystem.
**Strengths.** Mature modules; plan/state/drift; portable; can manage non-Azure too
(Langfuse infra, DNS); large talent pool.
**Weaknesses.** State to manage/secure; provider can lag brand-new Azure features
briefly.
**Cost / effort.** Medium.

### 5.2 Option B — Azure Bicep

**Description.** Azure-native DSL over ARM; no state file (ARM is the state).
**Strengths.** Azure-native, day-0 feature coverage; no state to manage; first-class MS
support/tooling; what-if preview.
**Weaknesses.** Azure-only (no portability/non-Azure providers); smaller module
ecosystem than Terraform; less mature drift tooling.
**Cost / effort.** Medium; simplest state.

### 5.3 Option C — ARM templates (raw JSON)

**Description.** Native ARM JSON.
**Strengths.** Fully native.
**Weaknesses.** Verbose; poor authoring ergonomics; Bicep supersedes it.
**Cost / effort.** High authoring cost.

### 5.4 Option D — Pulumi (general-purpose languages)

**Description.** IaC in Python/TS.
**Strengths.** Real languages; good for complex logic; state + preview.
**Weaknesses.** Smaller community than Terraform; another runtime; team less familiar.
**Cost / effort.** Medium.

### 5.5 Option E — Terraform CDK (CDKTF)

**Description.** Terraform via TypeScript/Python.
**Strengths.** Programmatic + Terraform providers.
**Weaknesses.** Extra abstraction over Terraform; less mature; smaller community.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Manual portal/CLI provisioning | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §42 — must be IaC |
| Ansible for cloud provisioning | Better for config mgmt than declarative cloud resources |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4 from tool documentation, Azure coverage and
team-skill considerations.

| Criterion | Weight | A: Terraform | B: Bicep | C: ARM JSON | D: Pulumi | E: CDKTF |
|---|---|---|---|---|---|---|
| EC-01 Azure coverage | 22 | 4 | 5 | 5 | 4 | 4 |
| EC-02 Module reuse | 20 | 5 | 4 | 2 | 4 | 4 |
| EC-03 State/plan/drift | 18 | 5 | 4 | 3 | 5 | 5 |
| EC-04 Team skills/standard | 16 | 5 | 4 | 2 | 3 | 3 |
| EC-05 Portability/ecosystem | 14 | 5 | 2 | 2 | 4 | 4 |
| EC-06 Ops simplicity | 10 | 3 | 5 | 3 | 3 | 3 |
| **Weighted total** | **100** | **454** | **404** | **288** | **388** | **392** |

Totals (×20): **A = 454**, **B = 404**, **E = 392**, **D = 388**, **C = 288**.

**Sensitivity.** Terraform leads Bicep by 50, driven by module ecosystem, portability
and talent pool. **If the criteria re-weight toward Azure-native day-0 coverage and
zero-state simplicity (EC-01+EC-06 up, EC-05 down), Bicep overtakes** — which is exactly
why this is `Proposed`: the platform team's house standard and skills decide it. Both
are sound; the loser is not wrong.

## 7. Decision

**PFF AI adopts the Enterprise Application's existing Infrastructure-as-Code approach and
delivery model (ADR-D5-20). It does not select or operate a separate IaC toolchain.**
Infrastructure is provisioned with the enterprise platform team's established tooling and
Azure DevOps `build.yaml`/`release.yaml` pipelines, on the shared enterprise AKS platform,
using the same team and resources — for consistency, supportability and to avoid a
parallel, divergent stack. If the enterprise standard is Terraform, PFF AI uses Terraform;
if Bicep, PFF AI uses Bicep — the point of this decision is *conformance with the
enterprise standard*, whatever it is, not an independent selection. The standalone
Terraform-recommended evaluation (§4–§6) stands as historical analysis but is not acted on
independently; ARM JSON (C), Pulumi (D) and CDKTF (E) remain not pursued.

**Status rationale.** `Accepted`. The gating condition — "platform-team house-standard
confirmation" (ADR-D0-04) — is met: the confirmed standard is to conform to the enterprise
application delivery model. This ADR moves out of `_register/open-decisions.md`. Any future
change to the IaC tool is an enterprise-platform decision that PFF AI follows, not a
PFF-AI-specific one.

## 8. Architecture Detail

> **Enterprise-conformant realization (ADR-D5-20):** the concrete IaC modules, state
> backend, pipeline stages and approvals are those of the Enterprise Application delivery
> model (Azure DevOps `build.yaml`/`release.yaml` → AKS), owned by the enterprise platform
> team. The structure below describes the shape of any PFF-AI-specific IaC that lives
> *within* that model; it does not create a separate stack.

- `infra/` holds IaC modules per resource group/service (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §43); environments
  (ADR-D5-14) compose modules with per-env variables (§40).
- Remote state in Azure Storage with locking; `plan` output reviewed in PRs before
  `apply` via CD (ADR-D7-10); drift detection scheduled.
- Secrets never in state where avoidable; state store access-controlled; Key Vault refs
  used (ADR-D5-07).
- K8s workloads are deployed by the manifest tool (ADR-D5-13), not IaC — IaC provisions
  the cluster/PaaS, manifests deploy apps.

## 9. Consequences

### 9.1 Positive
- Reproducible, reviewable, drift-detected infrastructure; portable modules.
### 9.2 Negative
- Remote state to secure/manage (Bicep would avoid this).
### 9.3 Neutral
- Pairs with manifest tool (D5-13) and env model (D5-14).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Bicep's zero-state simplicity | Modules + portability + talent pool | Platform Eng |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Infra tooling; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | IaC versioned in Git |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | State file compromise/corruption | Low | High | M | Access-controlled backend + locking + backup | Platform Eng | Low |
| RSK-02 | Provider lags a new Azure feature | Low | Low | L | Temporary Bicep/CLI for that resource | Platform Eng | Low |
| RSK-03 | Team unfamiliar → errors | Med | Med | M | Standards + review gate; or choose Bicep fallback | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Infra provisioned via IaC | 100% | < 100% | Audit | Per release |
| QM-02 | Drift incidents | ≈ 0 | rising | Drift detection | Weekly |
| QM-03 | Apply preceded by reviewed plan | 100% | < 100% | CD logs | Per apply |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | IaC enables consistent hardened baselines |
| Data classification touched | State may reference resource metadata (no secrets) |
| Personal data / PII | None in IaC |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Git history + plan/apply logs |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `infra/` |
| Configuration | Backend/state; per-env vars |
| Contracts / schemas | Module interfaces |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-08, D5-13, D5-14 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All Azure resources defined in IaC | Audit |
| AC-02 | Apply gated by reviewed plan | CD config |
| AC-03 | State access-controlled | Security review |
| AC-04 | Drift detection scheduled | Config |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Drift detection; apply outcomes |
| Alerting | Drift; failed apply |
| Runbook | `docs/runbooks/iac.md` |
| Failure mode and degradation | Failed apply → no partial live change (plan-gated) |
| Rollback | Revert IaC + re-apply |
| Support model impact | Platform + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| IaC tooling | none (OSS) | state storage | Terraform/OpenTofu OSS |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Team standardises on Azure-native | Team decision | Adopt Bicep (fallback) |
| RT-02 | Multi-cloud need arises | Strategy | Terraform's portability confirmed |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §42–§44 |
| Requirement IDs | INFRA-IAC-* |
| Build phases | 1 |
| Code paths | `infra/` |
| Configuration | backend/env vars |
| Tests | plan validation |
| Upstream ADRs | ADR-D5-08, D0-04 |
| Downstream ADRs | ADR-D5-13, D5-14 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Platform Engineer | Initial decision recorded — OPEN (Proposed); recommend Terraform, fallback Bicep. |
| 2.0.0 | 2026-09-05 | Platform Engineer | **Accepted.** Platform-team house-standard confirmed: PFF AI conforms to the Enterprise Application delivery model (ADR-D5-20) — Azure DevOps `build.yaml`/`release.yaml` on the shared AKS platform, same team and resources — rather than selecting a separate IaC tool. §1 and §7 rewritten to the enterprise-conformant decision; §4–§6 evaluation retained as history. Moved out of open-decisions. |
