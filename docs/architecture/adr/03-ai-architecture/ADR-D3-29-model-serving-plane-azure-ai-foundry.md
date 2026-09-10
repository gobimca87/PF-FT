---
id: ADR-D3-29
title: Model serving plane — Azure AI Foundry hosted-first, self-hosted vLLM as target
domain: 3 AI
ws_ref: [WS-16]
status: Proposed
version: 1.0.0
date: 2026-09-10
decision_owner: AI Solution Architect
contributors: [AI Architecture Lead, ML Engineer, Platform Engineer, Security Architect, FinOps]
reviewers: [Principal Architect, Data Protection Officer, Enterprise Architect]
approver: Architecture Review Board
supersedes: [ADR-D3-13]
superseded_by: []
related_adrs: [ADR-D3-13, ADR-D3-14, ADR-D3-15, ADR-D3-18, ADR-D3-23, ADR-D5-08, ADR-D5-10, ADR-D5-11, ADR-D6-01, ADR-D6-04, ADR-D6-07, ADR-D6-19]
source_docs:
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §2, §3, §4, §5, §19, §20, §21, §85, §103, §104, §105, §124, §125, §126"
  - "MD files/4 AI/14.PFF-FA-AI-EMBEDDING-VECTOR.md §11, §13"
  - "CLAUDE.md — Confirmed Tech Stack; Golden Rule"
build_phases: [6, 20]
impacted_paths:
  - src/pff_fa_ai/slm/
  - src/pff_fa_ai/embedding_vector/
  - config/base/slm.yaml
  - config/base/embedding.yaml
classification: Confidential
review_due: 2027-09-10
---

# ADR-D3-29 — Model serving plane — Azure AI Foundry hosted-first, self-hosted vLLM as target

> **Supersedes [ADR-D3-13](ADR-D3-13-slm-strategy-hosted-first-self-hosted-target.md).** ADR-D3-13
> selected the **Hugging Face Inference API** as the hosted-first provider. This ADR replaces that
> hosted-first provider with **Azure AI Foundry** (in-tenancy Azure), keeping the same phased strategy,
> the same provider-neutral abstraction (ADR-D3-14), and the same self-hosted vLLM-on-AKS target
> (ADR-D5-10). The *strategy* (hosted-first → self-hosted, behind an abstraction) is unchanged; only the
> *hosted provider* changes. Hugging Face is retained as an optional evaluation/experimentation provider.

## 1. Summary

PFF AI will use **Azure AI Foundry** as its hosted-first inference plane for both language generation
and embeddings, migrating to an **internally self-hosted SLM** (vLLM on AKS GPU — see
[ADR-D5-10](../05-technology-architecture/ADR-D5-10-self-hosted-slm-serving-stack.md)) as the target
state, all consumed only through the provider-neutral SLM/embedding abstraction
([ADR-D3-14](ADR-D3-14-slm-provider-abstraction.md)). Foundry runs in-tenancy in an Azure region under
the enterprise Enterprise Agreement / Data Processing Addendum, authenticated via Entra ID / managed
identity (aligning with the Key-Vault-via-SPN-only rule, ADR-D5-07) and reachable over Private Link
(ADR-D6-04). This keeps the fast time-to-value of a managed service **without** the external-egress data
boundary that the Hugging Face Inference API imposed, and unifies the hosted and self-hosted phases
inside one Azure platform. Provider choice never leaks past the abstraction, so both the day-one hosted
choice and the later self-host cutover are configuration changes, not rewrites.

## 2. Context and Problem Statement

ADR-D3-13 fixed the direction "Hugging Face Inference API → internal self-hosted SLM" per the (then)
`CLAUDE.md` tech-stack line and 15.PFF-FA-AI-SLM.md §5. Since then two facts have sharpened the decision:

1. **The enterprise is all-Azure, cloud-native.** APIM, Key Vault (MI-SPN only), AKS, Azure Managed
   Redis, Azure AI Search, Azure Service Bus, Azure Monitor and the Enterprise Application delivery
   model (ADR-D5-20) are already the platform. An external SaaS inference vendor (Hugging Face) is the
   one component that sits outside this boundary.
2. **The data-boundary posture is dominant.** ADR-D3-13 itself weighted data-boundary control at 22/100
   — the highest criterion — because of FA safeguarding/PII sensitivity (§124–§126). ADR-D6-19 then made
   masking **mandatory and fail-closed** for any *external* SLM. The Hugging Face Inference API is
   external egress, so it permanently carries that mandatory-masking cost, a DPIA, and a cross-border
   transfer assessment (ADR-D6-07).

Azure AI Foundry — the unified Azure model platform (Azure OpenAI models plus a catalog of open models
available as serverless "Models-as-a-Service" and managed-compute deployments) — was not evaluated as a
distinct option in ADR-D3-13: "Azure OpenAI" was folded into a rejected commercial-API option (its
Option C) and "Azure ML managed endpoints" into a self-host *how* (its Option D). Neither captured
Foundry's actual shape: an **in-tenancy managed plane that can host the same open small models** behind
the same abstraction, with a clean on-ramp to self-hosting.

What is blocked / goes wrong without this decision: the team either keeps building toward an external
provider that the data-boundary policy will force off for sensitive flows anyway (rework), or silently
switches provider without superseding the Accepted ADR-D3-13 (governance breach, per ADR-D0-01 and the
`CLAUDE.md` Golden-Rule discipline).

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Generate language for orchestration/communication (never business truth) | 15.PFF-FA-AI-SLM.md §2, §4, §40 |
| DR-F-02 | Provider-neutral access; swap providers without code change | 15.PFF-FA-AI-SLM.md §6, §15; ADR-D3-14 |
| DR-F-03 | Support fallback across providers/models | 15.PFF-FA-AI-SLM.md §62; ADR-D3-18 |
| DR-F-04 | Host both generation and embeddings on the same plane | 14.PFF-FA-AI-EMBEDDING-VECTOR.md §11; ADR-D3-23 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Time-to-first-value | Weeks, not GPU-platform months | 15.PFF-FA-AI-SLM.md §19 |
| DR-N-02 | Data boundary control | In-tenancy inference; no external egress of sensitive data | §124–§126; ADR-D6-07, ADR-D6-19 |
| DR-N-03 | Unit cost at volume | Managed now, self-host cheaper per token at scale | §103–§105 |
| DR-N-04 | Identity & network alignment | Entra ID / MI; Private Link | ADR-D5-07, ADR-D6-01, ADR-D6-04 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Hosted-first → self-hosted target, phased | Organisational | CLAUDE.md; 15.PFF-FA-AI-SLM.md §5 |
| DR-C-02 | SLM never executes business rules / makes authz | Regulatory/Arch | 15.PFF-FA-AI-SLM.md §4, §40 |
| DR-C-03 | Access only via provider abstraction | Architecture | ADR-D3-14; ADR-D2-01 |
| DR-C-04 | Key Vault only via enterprise SPN / managed identity | Security | ADR-D5-07, ADR-D5-20 |
| DR-C-05 | Conform to the enterprise Azure platform; no separate stack | Organisational | ADR-D5-20 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Foundry hosts a small model meeting quality on PFF-FA tasks | Use an Azure OpenAI model behind the abstraction, or bring self-host forward | SLM eval (15.PFF-FA-AI-SLM.md §92) |
| DR-A-02 | Foundry managed cost is acceptable until self-host break-even | Accelerate self-host cutover (ADR-D5-10) | Cost model (§106) |
| DR-A-03 | Foundry is available in the required Azure region with Private Link | Use regional fallback / managed compute | Platform review |

## 4. Evaluation Criteria and Weights

Weights are inherited from ADR-D3-13 (unchanged) so the two decisions are directly comparable.

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Time-to-value (initial) | 18 | Ship the first workflow fast | Setup lead time |
| EC-02 | Data-boundary control | 22 | FA/safeguarding data sensitivity | In-tenancy? egress? masking burden? |
| EC-03 | Quality on PFF-FA tasks | 18 | Must be good enough | Eval scores (§97) |
| EC-04 | Unit cost at target volume | 15 | Long-run economics | £/1k workflows (§106) |
| EC-05 | Operational burden | 12 | Managed vs GPU ops | Team effort/SRE load |
| EC-06 | Portability / no lock-in | 10 | Swap providers freely | Abstraction conformance; open-model optionality |
| EC-07 | Scalability & latency control | 5 | Own the tuning knobs later | p95 control |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Azure AI Foundry hosted-first, self-hosted vLLM as target (phased)

**Description.** Ship on Azure AI Foundry (serverless MaaS or managed compute) behind the abstraction;
build self-hosted vLLM/AKS GPU as the target (ADR-D5-10); cut over per-workflow when cost/quality
justify. Same open small-model family can run on both planes.
**Strengths.** Fast start with no early GPU ops; **in-tenancy** from day one (Entra ID, Private Link,
EA/DPA); one Azure control plane (Monitor, Content Safety, cost); clean, all-Azure on-ramp to
self-host; open-model optionality preserved behind the abstraction.
**Weaknesses.** Azure coupling (contained behind the abstraction); managed cost until self-host
break-even; some niche OSS models arrive in the catalog later than on Hugging Face.
**Cost / effort.** Low now, medium later (GPU platform).

### 5.2 Option B — Hugging Face Inference API hosted-first (the superseded ADR-D3-13 status quo)

**Description.** Keep HF Inference API as the hosted-first provider.
**Strengths.** Widest OSS model selection; lowest-friction experimentation; least vendor coupling.
**Weaknesses.** External egress → **mandatory fail-closed masking** (ADR-D6-19), DPIA and cross-border
transfer assessment for every sensitive flow; long-lived bearer token instead of managed identity;
public egress allowlist; a second SaaS vendor outside the Azure platform (against ADR-D5-20).
**Cost / effort.** Low now, but a permanent boundary/governance tax and a cross-vendor jump to self-host.

### 5.3 Option C — Azure OpenAI models only (no open-model / no self-host path)

**Description.** Use Azure OpenAI (GPT-class) in Foundry as the sole provider; drop the self-host target.
**Strengths.** Top quality; in-tenancy; fully managed; zero model ops.
**Weaknesses.** Higher per-token cost at volume with no self-host escape valve; strategic lock-in;
abandons the "small-model, self-hosted target" posture (§85, §103–§105) and ADR-D5-10.
**Cost / effort.** Low ops, high recurring; strategic misalignment.

### 5.4 Option D — Self-hosted vLLM from day one (no hosted phase)

**Description.** Stand up GPU serving immediately; no hosted phase at all.
**Strengths.** In-tenancy from the start; full control; best unit cost at volume.
**Weaknesses.** Heavy GPU ops before product validation; slow time-to-value; premature capacity/cost
commitment (§85).
**Cost / effort.** High up-front.

### 5.5 Option E — Dual hosted: Hugging Face + Azure AI Foundry

**Description.** Run both hosted providers behind the abstraction, routing by task/model.
**Strengths.** Maximum model choice; graceful provider failover.
**Weaknesses.** The HF leg keeps the external-egress boundary and its masking/DPIA cost; two hosted
providers to secure, monitor and govern permanently; premature before either leg is proven.
**Cost / effort.** Medium-high complexity; a later optimisation, not a starting posture.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No SLM (rules/templates only) | DR-F-01 — conversational orchestration needs generation |
| Non-Azure hosted vendor (e.g. Bedrock/Vertex) | DR-C-05 — enterprise is all-Azure; would add a second cloud |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, using the same weights as ADR-D3-13 so the provider change is
directly comparable, informed by §5, §19–§21, §85, §103–§106, §124–§126, ADR-D6-19 and the all-Azure
platform posture (ADR-D5-20).

| Criterion | Weight | A: Foundry→self-host | B: HF→self-host | C: Azure OpenAI only | D: Self-host day 1 | E: HF+Foundry dual |
|---|---|---|---|---|---|---|
| EC-01 Time-to-value | 18 | 5 | 5 | 5 | 2 | 4 |
| EC-02 Data boundary | 22 | 5 | 3 | 5 | 5 | 4 |
| EC-03 Quality | 18 | 5 | 4 | 5 | 4 | 5 |
| EC-04 Unit cost @ volume | 15 | 4 | 4 | 2 | 5 | 3 |
| EC-05 Ops burden | 12 | 4 | 4 | 5 | 2 | 3 |
| EC-06 Portability | 10 | 4 | 5 | 2 | 4 | 4 |
| EC-07 Scale/latency control | 5 | 4 | 4 | 3 | 5 | 4 |
| **Weighted total (max 500)** | **100** | **458** | **406** | **415** | **382** | **391** |

Totals: **A = 458**, **C = 415**, **B = 406**, **E = 391**, **D = 382**.

**Sensitivity.** A leads C by 43 and B (the superseded status quo) by 52. The gap between A and B is
driven almost entirely by EC-02: moving from external egress (B: 3, mandatory masking + DPIA) to
in-tenancy (A: 5). C (Azure OpenAI only) is the nearest rival but loses on EC-04/EC-06 because it drops
the self-host target and open-model optionality — A keeps both. Even if EC-02 were weighted lower, A
still leads on the combined ops/identity/network alignment (EC-05 + EC-04) for an all-Azure shop.
D only wins if unit cost (EC-04) dominated everything, which the time-to-value driver forbids for
Phase 1.

## 7. Decision

**PFF AI will adopt Azure AI Foundry as the hosted-first inference plane for language generation and
embeddings, with an internal self-hosted SLM (vLLM on AKS GPU, ADR-D5-10) as the target state**, both
behind the provider-neutral abstraction (ADR-D3-14). This **supersedes ADR-D3-13's selection of the
Hugging Face Inference API as the hosted-first provider**; the phased strategy, the abstraction, and the
self-host target are otherwise unchanged.

- **Hugging Face** is retained as an **optional evaluation/experimentation provider only** (offline model
  eval, benchmarking) — never a production/hosted path. If ever invoked at runtime it is `EXTERNAL`
  placement and subject to the mandatory masking boundary (ADR-D6-19).
- **Placement.** Foundry is `SlmPlacement.MANAGED_IN_TENANCY`: a managed Azure service running
  in-tenancy under the EA/DPA, so it takes the **self-hosted masking posture** (raw-or-masked per task
  class), **not** the mandatory external-egress boundary. This refines ADR-D6-19 (see §13).
- **Cutover to self-host** (ADR-D5-10) is per-workflow, gated on SLM evaluation (§92, §99), cost (§106)
  and data-boundary review — identical gates to ADR-D3-13; the Foundry managed plane is the on-ramp.

**Status rationale.** `Proposed` — this changes an Accepted decision and therefore awaits ARB sign-off
(with the DPO on the placement/masking refinement and FinOps on the Foundry cost model). Build against
this direction meanwhile, per the `CLAUDE.md` "Proposed = working default" rule.

## 8. Architecture Detail

- **Abstraction** (ADR-D3-14): unchanged `SLMProvider` / `EmbeddingProvider` protocols. New adapters
  `AzureAIFoundrySLMProvider` and `AzureAIFoundryEmbeddingProvider` call the OpenAI-compatible Azure AI
  Model Inference API (`/models/chat/completions`, `/embeddings`) via the shared httpx client; no
  provider SDK is imported past the adapter (ADR-D2-01). `HuggingFaceSLMProvider` /
  `HuggingFaceEmbeddingProvider` remain for eval only.
- **Identity/secrets** (ADR-D5-07): the shared client carries the Foundry endpoint + Entra ID /
  managed-identity credential resolved from Key Vault via `*_secret_ref`; no long-lived provider token
  in application config.
- **Network** (ADR-D6-04): Foundry reached over Private Link; no public egress allowlist for inference.
- **Placement & masking** (ADR-D6-19): `SlmPlacement.MANAGED_IN_TENANCY` added; the mandatory
  `MaskedExternalSLMProvider` boundary wraps only `EXTERNAL` providers, so Foundry is masked per task
  class like a self-hosted SLM.
- **Config** (config/base/slm.yaml, embedding.yaml): default provider stays `mock` until model eval +
  ARB sign-off; `azure_ai_foundry` documented as the hosted option with `endpoint_secret_ref` and pinned
  `model_version`.
- **Fallback** (ADR-D3-18): unchanged; ordered, logged, non-silent.
- **Cutover**: shadow eval → canary → cutover per workflow; rollback by config.

## 9. Consequences

### 9.1 Positive
- In-tenancy inference from day one → removes the mandatory external-masking/DPIA burden for hosted
  inference and materially lowers RSK (safeguarding/PII exposure).
- One Azure control plane (identity, network, monitoring, Content Safety, cost); aligns with ADR-D5-20.
- All-Azure on-ramp to self-host: the hosted→self-host transition no longer crosses a vendor boundary.
- Provider choice stays behind the abstraction → still a config change, and open-model optionality is
  preserved.

### 9.2 Negative
- Azure coupling for the hosted plane (mitigated by the abstraction and by open-model portability).
- Managed cost until self-host break-even; some niche OSS models arrive in the Foundry catalog later.

### 9.3 Neutral
- Self-host serving-stack choice remains ADR-D5-10 (vLLM on AKS GPU), now with Foundry managed compute
  as an explicit managed on-ramp/fallback.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Widest OSS breadth / lowest-friction experimentation of HF | In-tenancy boundary + Azure-native identity/network/ops | AI Solution Architect, DPO |
| Some hosted managed cost premium vs pay-per-call | Removal of external-egress governance tax; unified platform | FinOps |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | SLM generates language only; never business truth/authz (§4, §40) |
| Precedence chain | SLM output is the lowest tier; never overrides ERC/enterprise |
| Four-state separation | SLM is stateless compute; state lives elsewhere |
| Versioned artefacts | Model + config versioned (ADR-D3-15; §154–§155) |
| Adam/PFF Chat AI persona governs *how*, not *what* | Provider choice is invisible to persona/user |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Foundry model quality insufficient on PFF-FA tasks | Low | Med | M | Swap to Azure OpenAI model behind abstraction; eval gate | ML Eng | Low |
| RSK-02 | Foundry managed cost exceeds projection | Med | Med | M | Cost model (§106); accelerate self-host cutover (ADR-D5-10) | FinOps | Low |
| RSK-03 | Region/Private Link availability gap | Low | Med | M | Regional fallback / managed compute; platform review | Platform Eng | Low |
| RSK-04 | Placement misclassified → sensitive data treated as in-tenancy wrongly | Low | High | M | Placement is explicit config; masking-per-task-class tests; DPO review (ADR-D6-19) | Security Architect | Low |
| RSK-05 | Abstraction leaks provider specifics | Low | High | M | Import-linter + contract tests (ADR-D3-14) | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | SLM eval score on PFF-FA tasks | ≥ gate | < gate | Eval (§97, §99) | Every model release |
| QM-02 | p95 generation latency | within budget (ADR-D5-18) | breach | Langfuse | Continuous |
| QM-03 | £ per 1k workflows | tracked vs model | > projection | FinOps (§106) | Monthly |
| QM-04 | % inference in-tenancy (Foundry + self-host) | 100% for production flows | < 100% | Config audit | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Removes external SaaS inference dependency for production; Entra ID replaces long-lived token; Private Link removes public egress |
| Data classification touched | Up to Confidential/Personal — stays in-tenancy under EA/DPA |
| Personal data / PII | No external egress for hosted inference; masking per task class (refines ADR-D6-19) |
| Children's data and safeguarding | Safeguarding flows served in-tenancy from day one |
| UK GDPR lawful basis and rights impact | No cross-border transfer for hosted inference; DPIA simplified vs external provider |
| Audit and evidential requirements | Provider+model+version on every trace (Langfuse) |
| Standards touched | ISO/IEC 42001, 27001, EU AI Act, NIST AI RMF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (hosted inference on Foundry), 20 (self-host cutover) |
| Repository paths | `src/pff_fa_ai/slm/`, `src/pff_fa_ai/embedding_vector/`, `config/base/slm.yaml`, `config/base/embedding.yaml` |
| Configuration | Provider `azure_ai_foundry`; endpoint `*_secret_ref`; pinned model version |
| Contracts / schemas | Unchanged SLM/embedding contracts (ADR-D3-14) |
| Migration | Add Foundry adapters; HF demoted to eval; per-workflow shadow→canary→cutover to self-host |
| Dependencies on other ADRs | ADR-D3-14, ADR-D5-10, ADR-D5-07, ADR-D6-04, ADR-D6-19 |
| Effort estimate | S–M now, L for self-host |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No caller imports a provider SDK directly | Import-linter (ADR-D2-01) |
| AC-02 | Provider swap requires no domain code change | Contract test across mock/Foundry/HF |
| AC-03 | Foundry payloads authenticated via MI/Entra, endpoint from Key Vault | Config/secret-ref test (ADR-D5-07) |
| AC-04 | Foundry placement = MANAGED_IN_TENANCY; not wrapped by mandatory external mask | Placement + masking-routing test (ADR-D6-19) |
| AC-05 | Fallback is logged, never silent | Test (§64) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Latency/error/cost per provider; Langfuse spans; Azure Monitor for Foundry |
| Alerting | Foundry outage/throttle, latency breach, error spike |
| Runbook | `docs/runbooks/slm.md`, `docs/runbooks/slm-boundary.md` |
| Failure mode and degradation | Foundry down → fallback → degraded mode (§163, §168) |
| Rollback | Config revert to prior provider/model |
| Support model impact | ML platform team; SRE for self-host phase |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Azure AI Foundry (hosted) | setup | usage / provisioned throughput | §104; Azure pricing |
| Self-hosted GPU (later) | platform build | GPU node hours | §105; ADR-D5-11 |
| Foundry adapters + eval harness | S | low | Shared tooling |
| Removed: HF Inference API subscription | — | eliminated for production | Supersedes ADR-D3-13 |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Foundry cost exceeds self-host break-even | QM-03 | Accelerate self-host cutover (ADR-D5-10) |
| RT-02 | Foundry quality gate failing on available models | QM-01 | Switch to Azure OpenAI model behind abstraction, or bring self-host forward |
| RT-03 | A required model exists only outside Foundry | Architecture review | Evaluate via HF eval provider; consider self-host of that model |
| RT-04 | Multiple services/languages need the SLM | Architecture review | Introduce LLM gateway behind the same contract (ADR-D3-14 RT-01) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 SLM |
| Specification sections | 15.PFF-FA-AI-SLM.md §2–§5, §19–§21, §85, §103–§106, §124–§126; 14.PFF-FA-AI-EMBEDDING-VECTOR.md §11, §13 |
| Requirement IDs | SLM-STRAT-*, EMB-HOST-* |
| Build phases | 6, 20 |
| Code paths | `src/pff_fa_ai/slm/`, `src/pff_fa_ai/embedding_vector/` |
| Configuration | provider/endpoint config; secret refs |
| Tests | provider contract + placement/masking-routing suites |
| Upstream ADRs | ADR-D3-13 (superseded), ADR-D3-14 |
| Downstream ADRs | ADR-D5-10, ADR-D3-18, ADR-D3-23, ADR-D6-19 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-09-10 | AI Solution Architect | Initial decision recorded; supersedes ADR-D3-13 (hosted-first provider changed from Hugging Face Inference API to Azure AI Foundry). |
