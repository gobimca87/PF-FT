---
id: ADR-D5-08
title: Cloud platform and compute — Azure + AKS
domain: 5 Technology
ws_ref: [WS-24]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Platform Engineer, SRE, Security Architect]
reviewers: [AI Architecture Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-09, ADR-D5-11, ADR-D5-12, ADR-D5-13, ADR-D5-15, ADR-D6-04]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §3, §4, §9, §10, §11, §12, §20, §22, §54"
build_phases: [1, 21]
impacted_paths:
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-08 — Cloud platform and compute — Azure + AKS

## 1. Summary

PFF AI will run on **Microsoft Azure** with **Azure Kubernetes Service (AKS)** as the
compute platform, alongside APIM, Key Vault, Service Bus, ACR and Azure Monitor
(CLAUDE.md; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §3–§4, §10). AKS gives the container orchestration, GPU node pools
(ADR-D5-11), private networking and workload separation the platform needs while
staying inside the FA's Azure tenancy.

## 2. Context and Problem Statement

CLAUDE.md fixes Azure + AKS; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §3–§4 describe the target Azure architecture,
§9–§12 the container/AKS runtime and workload separation, §20–§22 CPU/GPU and network
architecture. The platform must co-locate with FA enterprise systems, support GPU
serving for the self-hosted SLM, provide private connectivity, and meet enterprise
security/compliance — all pointing to the FA's existing cloud. This ADR records the
platform choice and why alternatives were not taken.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Container orchestration with GPU node pools | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §10, §20–§21; ADR-D5-11 |
| DR-F-02 | Private connectivity to enterprise + PaaS | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §22–§24; ADR-D6-04 |
| DR-C-01 | Stay in the FA's Azure tenancy | CLAUDE.md; organisational |
| DR-N-01 | HA, autoscaling, workload separation | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §12, §52, §54 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | FA standardises on Azure | Re-evaluate platform | Enterprise architecture |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Enterprise/tenancy alignment | 28 | Co-location, compliance | FA cloud fit |
| EC-02 | GPU + container orchestration | 22 | SLM serving | GPU pools, K8s |
| EC-03 | Private networking + security | 20 | Enterprise bar | PE/RBAC |
| EC-04 | Managed PaaS ecosystem (APIM/KV/SB) | 16 | Integrations | Native services |
| EC-05 | Ops maturity/skills/cost | 14 | Run it | Skills/cost |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Azure + AKS

**Description.** AKS for compute; APIM, Key Vault, Service Bus, ACR, Monitor; GPU node
pools; private endpoints.
**Strengths.** FA tenancy alignment; full PaaS ecosystem the stack already names;
GPU + K8s; private networking.
**Weaknesses.** K8s operational complexity (managed by AKS).
**Cost / effort.** Aligned with existing skills/estate.

### 5.2 Option B — Azure Container Apps (serverless containers)

**Description.** Azure Container Apps instead of AKS.
**Strengths.** Less K8s ops; scale-to-zero.
**Weaknesses.** Less control over GPU serving/node pools; weaker fit for self-hosted
SLM and fine-grained workload separation (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §12, §21).
**Cost / effort.** Lower ops, less control.

### 5.3 Option C — AWS + EKS

**Description.** AWS platform.
**Strengths.** Mature K8s/GPU.
**Weaknesses.** Off the FA's Azure tenancy; re-do enterprise connectivity/compliance;
stack (APIM/KV/SB) is Azure-named. Cross-cloud to enterprise systems.
**Cost / effort.** High migration/integration cost.

### 5.4 Option D — GCP + GKE

**Description.** Google Cloud.
**Strengths.** Strong K8s/AI.
**Weaknesses.** Same off-tenancy objections as C.
**Cost / effort.** High.

### 5.5 Option E — Azure VMs (IaaS, self-managed orchestration)

**Description.** Run containers on plain VMs.
**Strengths.** Full control.
**Weaknesses.** Re-implement orchestration/scaling/HA that AKS provides; high ops.
**Cost / effort.** High ops.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| On-prem Kubernetes | Doesn't meet cloud/scale/PaaS needs |
| Multi-cloud active-active | Unwarranted complexity now (portability in ADR-D8-10) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by CLAUDE.md and 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §3–§22.

| Criterion | Weight | A: Azure+AKS | B: Container Apps | C: AWS+EKS | D: GCP+GKE | E: Azure VMs |
|---|---|---|---|---|---|---|
| EC-01 Tenancy alignment | 28 | 5 | 5 | 1 | 1 | 5 |
| EC-02 GPU+orchestration | 22 | 5 | 3 | 5 | 5 | 3 |
| EC-03 Private net/security | 20 | 5 | 4 | 3 | 3 | 4 |
| EC-04 PaaS ecosystem | 16 | 5 | 5 | 2 | 2 | 5 |
| EC-05 Ops/skills/cost | 14 | 4 | 5 | 3 | 3 | 2 |
| **Weighted total** | **100** | **484** | **432** | **288** | **288** | **396** |

Totals (×20): **A = 484**, **B = 432**, **E = 396**, **C = 288**, **D = 288**.

**Sensitivity.** A leads B by 52; B (Container Apps) is the only serious Azure
alternative but loses on GPU/workload-separation control needed for self-hosted SLM.
Non-Azure (C/D) fail tenancy alignment decisively. Container Apps may still host
stateless CPU-only workers later where scale-to-zero helps (RT-01).

## 7. Decision

**PFF AI will run on Azure with AKS as the compute platform**, using APIM (ADR-D5-15),
Key Vault (ADR-D5-07), Service Bus (ADR-D2-16), ACR (ADR-D5-09) and Azure Monitor
(ADR-D7-01), with GPU node pools (ADR-D5-11) and private networking (ADR-D6-04).
Container Apps (B) may host stateless CPU workers later; AWS/GCP (C/D) and plain VMs
(E) are rejected.

**Status rationale.** `Accepted` — confirmed in CLAUDE.md and 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md.

## 8. Architecture Detail

- AKS cluster with node pools: system, CPU workload, GPU workload (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §12, §20–§21);
  namespace strategy per environment (§11); pod distribution/HA (§54–§55).
- Private cluster / private endpoints (§24; ADR-D6-04); egress control (§25).
- IaC provisions all of it (ADR-D5-12); K8s manifests deploy workloads (ADR-D5-13).

## 9. Consequences

### 9.1 Positive
- Tenancy-aligned, GPU-capable, PaaS-rich, privately-networked platform.
### 9.2 Negative
- AKS/K8s operational complexity (mitigated by managed control plane + IaC).
### 9.3 Neutral
- Anchors infra ADRs (D5-09/11/12/13/14/15).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Serverless simplicity (Container Apps) | GPU/workload-separation control | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Platform hosts the AI layer; enterprise systems remain authoritative |
| Precedence chain | N/A (infra) |
| Four-state separation | Workloads separated by node pool/namespace |
| Versioned artefacts | Infra as code, versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | K8s ops burden | Med | Med | M | Managed AKS + IaC + runbooks | SRE | Low |
| RSK-02 | GPU capacity constraints | Med | Med | M | GPU node pool planning (ADR-D5-11) | Platform Eng | Low |
| RSK-03 | Cloud lock-in | Med | Low | L | Portability strategy (ADR-D8-10) | Principal Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Cluster availability | ≥ 99.9% | < 99.5% | Azure Monitor | Monthly |
| QM-02 | Workload separation adherence | 100% | < 100% | Config audit | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Private cluster, controlled egress (ADR-D6-04) |
| Data classification touched | Internal |
| Personal data / PII | Hosted within FA Azure tenancy/region |
| Children's data and safeguarding | Data residency in-tenancy |
| UK GDPR lawful basis and rights impact | Data residency supports compliance |
| Audit and evidential requirements | Azure activity + cluster logs |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 (base), 21 (GPU/self-host) |
| Repository paths | `infra/` |
| Configuration | AKS/node-pool config via IaC |
| Contracts / schemas | N/A |
| Migration | N/A (greenfield) |
| Dependencies on other ADRs | ADR-D5-09, D5-11, D5-12, D5-13, D5-15 |
| Effort estimate | L |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Workloads on correct node pools | Config audit |
| AC-02 | Private networking enforced | Network review (ADR-D6-04) |
| AC-03 | GPU pool available for SLM | Provisioning test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Cluster/node/pod metrics (ADR-D7-01) |
| Alerting | Node/pool health; capacity |
| Runbook | `docs/runbooks/aks.md` |
| Failure mode and degradation | Pod/node failover; HA distribution (§54–§55) |
| Rollback | IaC/manifest revert |
| Support model impact | SRE + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| AKS cluster + nodes | setup | node hours | Azure pricing |
| GPU nodes | — | GPU hours | ADR-D5-11 |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Stateless CPU workers benefit from scale-to-zero | Cost/ops | Host those on Container Apps |
| RT-02 | FA cloud strategy changes | Enterprise | Re-evaluate platform |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 Infrastructure |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §3–§4, §9–§12, §20–§25, §54 |
| Requirement IDs | INFRA-PLAT-* |
| Build phases | 1, 21 |
| Code paths | `infra/` |
| Configuration | AKS IaC |
| Tests | provisioning/network tests |
| Upstream ADRs | — |
| Downstream ADRs | ADR-D5-09, D5-11, D5-12, D5-13, D5-15 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
