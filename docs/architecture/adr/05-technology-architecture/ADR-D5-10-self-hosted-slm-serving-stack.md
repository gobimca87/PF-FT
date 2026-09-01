---
id: ADR-D5-10
title: Self-hosted SLM serving stack — vLLM vs TGI vs Azure ML
domain: 5 Technology
ws_ref: [WS-24]
status: Proposed
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Platform Engineer, SRE, FinOps]
reviewers: [Principal Architect, Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-13, ADR-D3-14, ADR-D3-17, ADR-D5-08, ADR-D5-11, ADR-D0-04]
source_docs:
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §5, §20, §21, §46, §47, §70, §71, §73, §77, §78, §80, §81"
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §20, §21"
build_phases: [20]
impacted_paths:
  - src/pff_fa_ai/slm/
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-10 — Self-hosted SLM serving stack — vLLM vs TGI vs Azure ML

> **OPEN DECISION** (`status: Proposed`, per [ADR-D0-04](../00-decision-programme/ADR-D0-04-open-decision-register-and-escalation.md)
> and CLAUDE.md). Full evaluation and a recommendation are given; final selection
> awaits a benchmark on the chosen model and is gated at build Phase 20 (self-host
> cutover). Not to be treated as Accepted.

## 1. Summary

For the self-hosted SLM phase (ADR-D3-13), PFF AI will serve the model on a
GPU-accelerated inference server behind the provider abstraction (ADR-D3-14). The
**recommendation is vLLM** for its PagedAttention throughput, continuous batching,
OpenAI-compatible API and broad model/quantisation support, with **Hugging Face TGI**
as the close fallback. The decision is `Proposed` pending a throughput/latency/quality
benchmark on the selected model and Azure GPU node type.

## 2. Context and Problem Statement

15.PFF-FA-AI-SLM.md §5/§20–§21 describe the future self-hosted architecture and its
responsibilities; §46–§47 inference/streaming; §70–§73 GPU/VRAM/quantisation; §77–§81
KV cache, scaling, warm-up, rolling deploy; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §20–§21 CPU/GPU strategy and SLM
infrastructure. CLAUDE.md lists the serving stack (vLLM or HF TGI) as still open. The
serving engine determines throughput per GPU (cost), latency, streaming/structured-
output support (ADR-D3-17/19), quantisation options and operational model. This ADR
evaluates the candidates and recommends one, to be confirmed by benchmark.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | High-throughput GPU serving (continuous batching) | 15.PFF-FA-AI-SLM.md §49–§51, §78; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §21 |
| DR-F-02 | Streaming + structured/constrained output support | 15.PFF-FA-AI-SLM.md §47–§48; ADR-D3-17/19 |
| DR-F-03 | Behind provider abstraction (OpenAI-compatible helps) | ADR-D3-14 |
| DR-N-01 | Throughput per GPU (unit cost) | 15.PFF-FA-AI-SLM.md §105; ADR-D5-11 |
| DR-N-02 | Quantisation + VRAM efficiency | 15.PFF-FA-AI-SLM.md §73–§77 |
| DR-C-01 | Runs on AKS GPU nodes in-tenancy | ADR-D5-08 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Chosen model is supported by the engine | Pick supported model/engine | Benchmark |
| DR-A-02 | Constrained decoding needed for structured output | Rely on validate+repair (ADR-D3-17) | Structured-output eval |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Throughput / GPU efficiency | 26 | Cost + capacity | tokens/s/GPU (benchmark) |
| EC-02 | Latency (TTFT + per-token) | 20 | UX (ADR-D5-18) | p95 latency |
| EC-03 | Feature fit (stream, structured/constrained, tools) | 18 | ADR-D3-17/19 | Feature support |
| EC-04 | Operability on AKS (deploy/scale/observability) | 16 | Run it | Ops fit |
| EC-05 | Model/quantisation coverage | 12 | Flexibility | Supported models/quant |
| EC-06 | Community/maturity/support | 8 | Longevity | Adoption |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — vLLM

**Description.** vLLM server on AKS GPU nodes; PagedAttention + continuous batching;
OpenAI-compatible API; supports many HF models + quantisation (AWQ/GPTQ) and guided/
grammar decoding.
**Strengths.** Best-in-class throughput; low latency under load; OpenAI-compatible
(clean adapter behind ADR-D3-14); constrained decoding for structured output
(ADR-D3-17); active community.
**Weaknesses.** You operate it (HA, upgrades) — shared across all options.
**Cost / effort.** Best throughput → lowest £/token; medium ops.

### 5.2 Option B — Hugging Face Text Generation Inference (TGI)

**Description.** HF TGI server on AKS GPU.
**Strengths.** Strong throughput (continuous batching); tight HF ecosystem fit (matches
ADR-D3-13 HF-first); streaming; production-grade.
**Weaknesses.** Licence terms have shifted historically; guided-decoding/features vary
by version; often slightly behind vLLM on peak throughput.
**Cost / effort.** Close to vLLM.

### 5.3 Option C — Azure Machine Learning managed online endpoints

**Description.** Deploy the model on Azure ML managed endpoints (which can host vLLM/
TGI containers under the hood).
**Strengths.** Managed control plane (less raw K8s ops); Azure-native; autoscaling.
**Weaknesses.** Less low-level control; another platform; can be costlier; still picks
an engine underneath. A *hosting choice*, not a distinct engine.
**Cost / effort.** Lower ops, less control.

### 5.4 Option D — NVIDIA Triton Inference Server (+ TensorRT-LLM)

**Description.** Triton with a TensorRT-LLM backend.
**Strengths.** Very high optimised throughput; multi-model; enterprise-grade.
**Weaknesses.** Heavier to configure; TensorRT-LLM engine build/maintenance per model;
steeper learning curve.
**Cost / effort.** High setup; strong at scale.

### 5.5 Option E — Ray Serve (with a vLLM/HF backend)

**Description.** Ray Serve orchestrating model replicas.
**Strengths.** Flexible scaling/composition; Python-native.
**Weaknesses.** Adds Ray as a platform to run; overkill for a single-model serving need
now; still wraps an engine.
**Cost / effort.** Higher platform complexity.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| llama.cpp/CPU-only serving | Throughput/latency inadequate for concurrent enterprise load |
| Bespoke Transformers `generate()` server | No continuous batching; poor throughput (§78) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4 from engine documentation and published
benchmarks; **scores are pre-benchmark expectations** to be confirmed on the selected
model + Azure GPU SKU (the `Proposed` gate).

| Criterion | Weight | A: vLLM | B: TGI | C: Azure ML | D: Triton+TRT-LLM | E: Ray Serve |
|---|---|---|---|---|---|---|
| EC-01 Throughput | 26 | 5 | 4 | 4 | 5 | 4 |
| EC-02 Latency | 20 | 5 | 4 | 4 | 5 | 4 |
| EC-03 Feature fit | 18 | 5 | 4 | 4 | 4 | 4 |
| EC-04 Operability on AKS | 16 | 4 | 4 | 5 | 3 | 3 |
| EC-05 Model/quant coverage | 12 | 5 | 4 | 4 | 4 | 4 |
| EC-06 Maturity | 8 | 5 | 5 | 5 | 5 | 4 |
| **Weighted total** | **100** | **484** | **408** | **424** | **436** | **384** |

Totals (×20): **A = 484**, **D = 436**, **C = 424**, **B = 408**, **E = 384**.

**Sensitivity.** vLLM leads, but the top four are within one benchmark of each other on
throughput/latency — hence `Proposed` pending a real benchmark. If operability
dominates (small team, prefer managed), **Azure ML (C) hosting a vLLM container** is
the pragmatic middle path and the likely fallback; Triton (D) wins only if peak
throughput at scale becomes the overriding concern.

## 7. Decision

**Recommendation: serve the self-hosted SLM with vLLM on AKS GPU nodes, behind the
provider abstraction (ADR-D3-14), using its OpenAI-compatible API and guided decoding
for structured output (ADR-D3-17).** Fallbacks, in order: Azure ML managed endpoints
hosting a vLLM/TGI container (C) if managed operability is preferred; HF TGI (B) for
tightest HF-ecosystem fit; Triton+TensorRT-LLM (D) if peak throughput at scale
dominates. Ray Serve (E) and CPU/bespoke serving are not pursued.

**Status rationale.** `Proposed` per ADR-D0-04/CLAUDE.md: the serving stack is an open
decision. Selection is confirmed by a throughput/latency/quality benchmark on the
chosen model and Azure GPU SKU, gated at Phase 20; listed in
`_register/open-decisions.md`. Not Accepted.

## 8. Architecture Detail

- A `SelfHostedProvider` adapter (ADR-D3-14) targets the engine's OpenAI-compatible
  endpoint; model registry (ADR-D3-15) records engine + model + quantisation.
- GPU node pool + VRAM planning (ADR-D5-11; 15.PFF-FA-AI-SLM.md §70–§77); KV cache (§77); warm-up
  (§80); rolling deploy + smoke test (§81–§82); autoscaling (§79; ADR-D5-17).
- Quantisation registry + evaluation (§75–§76) before promoting a quantised model.
- Benchmark harness measures tokens/s/GPU, TTFT, p95, and eval quality per engine on
  the target SKU — the evidence that discharges `Proposed`.

## 9. Consequences

### 9.1 Positive
- High-throughput, low-latency, in-tenancy serving with structured-output support.
### 9.2 Negative
- Operating a GPU inference service; final engine pending benchmark.
### 9.3 Neutral
- Adapter isolates the choice; swapping engines is a provider swap (ADR-D3-14).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Managed simplicity (if vLLM self-run) | Throughput + control + lower £/token | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Serving engine runs generation only; no business authority |
| Precedence chain | SLM output remains lowest authority |
| Four-state separation | Stateless inference |
| Versioned artefacts | Engine+model+quant versioned in registry/manifest |
| Adam persona governs *how*, not *what* | Engine invisible to persona |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Chosen engine underperforms on target SKU | Med | Med | M | Benchmark before commit (Proposed gate) | ML Eng | Low |
| RSK-02 | GPU capacity/cost overrun | Med | High | H | Quantisation + autoscaling + FinOps gate | FinOps | Med |
| RSK-03 | Engine feature gap (structured/constrained) | Low | Med | M | Validate+repair fallback (ADR-D3-17) | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Tokens/s/GPU | ≥ benchmark target | below | Benchmark/metrics | Per model change |
| QM-02 | p95 generation latency | within budget (ADR-D5-18) | breach | App Insights | Continuous |
| QM-03 | GPU utilisation | healthy band | low/thrash | GPU metrics | Continuous |
| QM-04 | £ per 1k workflows (self-host) | ≤ model | > projection | FinOps | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | In-tenancy inference removes external data egress (vs HF API) |
| Data classification touched | Up to Confidential/Personal — now in-tenancy |
| Personal data / PII | Stays in Azure; boundary tightened vs external API |
| Children's data and safeguarding | Safeguarding flows can run fully in-tenancy |
| UK GDPR lawful basis and rights impact | Improves data residency posture |
| Audit and evidential requirements | Engine+model+version traced |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 20 (self-host cutover) |
| Repository paths | `src/pff_fa_ai/slm/`, `infra/` |
| Configuration | Engine/model/quant config; GPU node pool |
| Contracts / schemas | SelfHostedProvider adapter |
| Migration | Per-workflow cutover from HF API (ADR-D3-13) |
| Dependencies on other ADRs | ADR-D3-13, D3-14, D5-08, D5-11 |
| Effort estimate | L |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Benchmark confirms engine meets throughput/latency/quality | Benchmark run (Proposed gate) |
| AC-02 | Adapter conforms to provider contract | Contract test (ADR-D3-14) |
| AC-03 | Structured output works (guided or validate+repair) | Eval (ADR-D3-17) |
| AC-04 | Runs on AKS GPU pool in-tenancy | Deployment test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | GPU util, tokens/s, latency, VRAM, queue depth |
| Alerting | Latency/throughput/VRAM breaches |
| Runbook | `docs/runbooks/slm-serving.md` |
| Failure mode and degradation | Serving down → fallback to HF API/other (ADR-D3-18) |
| Rollback | Rolling deploy rollback (§81, §159) |
| Support model impact | ML platform + SRE (GPU on-call) |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Serving engine | none (OSS) | — | vLLM/TGI OSS |
| GPU nodes | platform | GPU hours | ADR-D5-11 |
| Azure ML (if fallback C) | setup | endpoint hours | Azure ML pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Benchmark favours another engine | Benchmark | Select fallback (C/B/D) |
| RT-02 | Scale demands peak throughput | Capacity | Evaluate Triton+TRT-LLM (D) |
| RT-03 | GPU cost unsustainable | QM-04 | Quantise further / rightsize / revisit HF API mix |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 |
| Specification sections | 15.PFF-FA-AI-SLM.md §5, §20–§21, §46–§47, §70–§81; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §20–§21 |
| Requirement IDs | SLM-SERVE-* |
| Build phases | 20 |
| Code paths | `src/pff_fa_ai/slm/`, `infra/` |
| Configuration | engine/GPU config |
| Tests | benchmark + contract + eval |
| Upstream ADRs | ADR-D3-13, D3-14, D5-08, D5-11, D0-04 |
| Downstream ADRs | ADR-D3-17, D5-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded — OPEN (Proposed); recommend vLLM, fallback Azure ML/TGI/Triton. |
