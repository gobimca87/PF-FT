---
id: ADR-D5-11
title: GPU node pool and CPU/GPU workload separation
domain: 5 Technology
ws_ref: [WS-24]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Platform Engineer
contributors: [ML Engineer, SRE, FinOps]
reviewers: [Principal Architect, AI Architecture Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-08, ADR-D5-10, ADR-D5-17, ADR-D3-13]
source_docs:
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §12, §19, §20, §21, §51, §52"
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §70, §71, §72, §78, §79"
build_phases: [20]
impacted_paths:
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-11 — GPU node pool and CPU/GPU workload separation

## 1. Summary

PFF AI will run CPU workloads (API, orchestration, workers) and GPU workloads
(self-hosted SLM/embedding inference) on **separate AKS node pools**, with the GPU pool
**independently autoscaled** and provisioned only when self-hosting is active (25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md
§12, §19–§21, §51–§52; 15.PF-FT-AI-SLM.md §70–§79). This keeps expensive GPUs saturated by
inference alone and lets the cheap CPU tier scale on request load independently.

## 2. Context and Problem Statement

25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §12 requires workload separation, §19 resource requests/limits, §20–§21 CPU/GPU
strategy and SLM infrastructure, §51–§52 scaling/autoscaling; 15.PF-FT-AI-SLM.md §70–§79 GPU/VRAM/
scaling. Mixing CPU and GPU workloads on one pool wastes GPU (idle while serving HTTP)
or starves inference; it also couples unrelated scaling signals. This ADR fixes the
node-pool topology and CPU/GPU separation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Separate CPU and GPU node pools | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §12, §20 |
| DR-F-02 | Independent autoscaling per pool | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §51–§52; ADR-D5-17 |
| DR-N-01 | GPU utilisation / VRAM efficiency | 15.PF-FT-AI-SLM.md §70–§77 |
| DR-C-01 | GPU provisioned only for self-host phase | ADR-D3-13 (phased) |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Azure GPU SKUs available in region | Alternative SKU/region | Capacity check |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | GPU cost efficiency/utilisation | 30 | GPUs are the cost driver | Utilisation % |
| EC-02 | Independent scaling correctness | 22 | Right signal per tier | Scaling behaviour |
| EC-03 | Isolation/reliability | 18 | No CPU/GPU contention | Contention incidents |
| EC-04 | Operability | 16 | Manage pools | Ops fit |
| EC-05 | Flexibility (phased GPU) | 14 | GPU only when needed | Provision on demand |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Separate CPU + GPU node pools, independently autoscaled; GPU provisioned at self-host phase

**Description.** Distinct pools with taints/tolerations + node selectors; GPU pool
autoscales on inference load, CPU pool on request load; GPU pool created only when
self-hosting begins.
**Strengths.** Max GPU utilisation; independent scaling; cost-controlled; isolated.
**Weaknesses.** Two pools to manage; scheduling config.
**Cost / effort.** Medium; best cost control.

### 5.2 Option B — Single mixed pool (CPU+GPU nodes together)

**Description.** One pool with GPU nodes.
**Strengths.** Simpler.
**Weaknesses.** GPU nodes run CPU pods (waste) or vice versa; coupled scaling; poor
utilisation.
**Cost / effort.** Low; wasteful.

### 5.3 Option C — GPU on separate managed service (Azure ML), CPU on AKS

**Description.** CPU on AKS; GPU inference on Azure ML endpoints (ties to ADR-D5-10 C).
**Strengths.** Managed GPU ops; independent scaling.
**Weaknesses.** Two platforms; cross-service networking; engine choice constrained by
ADR-D5-10.
**Cost / effort.** Medium; depends on D5-10.

### 5.4 Option D — Serverless GPU (e.g. Azure Container Apps GPU / spot)

**Description.** On-demand/spot GPU.
**Strengths.** Scale-to-zero; low idle cost.
**Weaknesses.** Cold-start latency; spot eviction; less control for steady inference.
**Cost / effort.** Low idle, variable reliability.

### 5.5 Option E — Separate pools + GPU time-slicing/MIG for small models

**Description.** Option A plus GPU partitioning (MIG/time-slicing) to pack small models.
**Strengths.** Higher GPU density for small SLMs.
**Weaknesses.** Added complexity; benefit depends on model size; a later optimisation
on A.
**Cost / effort.** Medium; premature.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| CPU-only (no GPU) | Self-hosted SLM needs GPU (ADR-D3-13) |
| GPU-only cluster | CPU workloads dominate request path |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §12/§20–§21/§51–§52 and 15.PF-FT-AI-SLM.md §70–§79.

| Criterion | Weight | A: Separate pools | B: Mixed pool | C: GPU on Azure ML | D: Serverless GPU | E: Pools + MIG |
|---|---|---|---|---|---|---|
| EC-01 GPU efficiency | 30 | 5 | 2 | 4 | 4 | 5 |
| EC-02 Independent scaling | 22 | 5 | 2 | 5 | 4 | 5 |
| EC-03 Isolation | 18 | 5 | 2 | 5 | 3 | 4 |
| EC-04 Operability | 16 | 4 | 4 | 4 | 3 | 3 |
| EC-05 Flexibility | 14 | 5 | 3 | 4 | 5 | 4 |
| **Weighted total** | **100** | **484** | **250** | **440** | **384** | **446** |

Totals (×20): **A = 484**, **E = 446**, **C = 440**, **D = 384**, **B = 250**.

**Sensitivity.** A leads; E (MIG/time-slicing) is a natural later optimisation for
small models (RT-01); C aligns if ADR-D5-10 selects Azure ML. B is clearly wasteful.

## 7. Decision

**PFF AI will use separate CPU and GPU node pools on AKS, independently autoscaled,
with the GPU pool provisioned at the self-host phase (Option A).** GPU scheduling uses
taints/tolerations + node selectors; VRAM/quantisation planning per 15.PF-FT-AI-SLM.md §70–§77. GPU
partitioning (E) may be added for small models; if ADR-D5-10 selects Azure ML, GPU
serving moves there (C) while CPU stays on AKS. Mixed pool (B) is rejected.

**Status rationale.** `Accepted` — 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §12/§20 mandate separation. (GPU *engine* is
open in ADR-D5-10; the *topology* here is settled.)

## 8. Architecture Detail

- Node pools: `system`, `cpu-workload`, `gpu-workload` (25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §11–§12); GPU nodes
  tainted so only inference pods schedule there; resource requests/limits set (§19).
- GPU pool autoscaler tuned to inference queue/utilisation (ADR-D5-17; 15.PF-FT-AI-SLM.md §79);
  warm-up on scale-up (15.PF-FT-AI-SLM.md §80).
- VRAM planning + quantisation (15.PF-FT-AI-SLM.md §72–§77) sizes the GPU SKU.

## 9. Consequences

### 9.1 Positive
- GPUs saturated by inference; CPU scales on requests; cost-controlled; isolated.
### 9.2 Negative
- Two pools + scheduling config to manage.
### 9.3 Neutral
- Interlocks with serving-stack (D5-10) and autoscaling (D5-17).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single-pool simplicity | GPU efficiency + isolation | Platform Eng |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Infra topology; no business authority |
| Precedence chain | N/A |
| Four-state separation | Workload separation, not data-state |
| Versioned artefacts | Node-pool config in IaC |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | GPU under-utilised (cost) | Med | High | H | Autoscale + right-size + quantise + MIG later | FinOps | Med |
| RSK-02 | GPU capacity shortage in region | Med | Med | M | Capacity reservation / alt SKU | Platform Eng | Low |
| RSK-03 | CPU pods scheduled on GPU nodes | Low | Med | M | Taints/tolerations + node selectors | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | GPU utilisation | healthy band | chronically low | GPU metrics | Weekly |
| QM-02 | CPU/GPU pod placement correctness | 100% | < 100% | Scheduler audit | Per release |
| QM-03 | GPU cost per 1k workflows | ≤ model | > projection | FinOps | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Isolated GPU workloads |
| Data classification touched | Inference data in-tenancy |
| Personal data / PII | Processed on in-tenancy GPUs |
| Children's data and safeguarding | In-tenancy processing |
| UK GDPR lawful basis and rights impact | Data residency |
| Audit and evidential requirements | Node/pod scheduling logged |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 20 |
| Repository paths | `infra/` |
| Configuration | Node pools, taints, autoscaler |
| Contracts / schemas | N/A |
| Migration | Add GPU pool at self-host |
| Dependencies on other ADRs | ADR-D5-08, D5-10, D5-17 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Separate CPU/GPU pools exist | Config audit |
| AC-02 | Inference pods only on GPU pool | Scheduler test |
| AC-03 | Pools autoscale independently | Load test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | GPU/CPU utilisation, VRAM, autoscale events |
| Alerting | Low GPU util; capacity; misplacement |
| Runbook | `docs/runbooks/gpu.md` |
| Failure mode and degradation | GPU pool issue → SLM fallback (ADR-D3-18) |
| Rollback | IaC revert |
| Support model impact | SRE (GPU) + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| GPU nodes | reservation | GPU hours | Azure GPU SKU pricing |
| CPU nodes | — | node hours | Azure pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Small models under-fill a GPU | QM-01 | Adopt MIG/time-slicing (Option E) |
| RT-02 | GPU idle cost high | QM-03 | Consider serverless/spot for bursty load |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 |
| Specification sections | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §12, §19–§21, §51–§52; 15.PF-FT-AI-SLM.md §70–§79 |
| Requirement IDs | INFRA-GPU-* |
| Build phases | 20 |
| Code paths | `infra/` |
| Configuration | node pools/autoscaler |
| Tests | scheduling/scaling tests |
| Upstream ADRs | ADR-D5-08, D5-10 |
| Downstream ADRs | ADR-D5-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Platform Engineer | Initial decision recorded. |
