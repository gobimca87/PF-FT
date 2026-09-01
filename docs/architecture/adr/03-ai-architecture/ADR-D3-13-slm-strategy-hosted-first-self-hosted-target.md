---
id: ADR-D3-13
title: SLM strategy — Hugging Face Inference API first, self-hosted SLM as target
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Platform Engineer, Security Architect, FinOps]
reviewers: [Principal Architect, Data Protection Officer]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-14, ADR-D3-15, ADR-D3-18, ADR-D5-10, ADR-D5-11, ADR-D6-07]
source_docs:
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §2, §3, §4, §5, §19, §20, §21, §85, §103, §104, §105, §124, §125, §126"
build_phases: [6, 20]
impacted_paths:
  - src/pff_fa_ai/slm/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D3-13 — SLM strategy — Hugging Face Inference API first, self-hosted SLM as target

## 1. Summary

PFF AI will start on the **Hugging Face Inference API** for language generation and
migrate to an **internally self-hosted SLM** (vLLM/TGI on AKS GPU — see
[ADR-D5-10](../05-technology-architecture/ADR-D5-10-self-hosted-slm-serving-stack.md))
as the target state, both consumed only through a provider-neutral SLM abstraction
([ADR-D3-14](ADR-D3-14-slm-provider-abstraction.md)). This buys fast time-to-value
without GPU operations up front while committing to bring inference in-tenancy for
data-boundary control and unit-cost at scale. Provider choice never leaks past the
abstraction, so the migration is a configuration change, not a rewrite.

## 2. Context and Problem Statement

15.PFF-FA-AI-SLM.md §5 defines "initial and future architecture" and §19–§21 describe the HF
integration now and self-hosted later; `CLAUDE.md` §Tech Stack fixes the direction
"Hugging Face Inference API → internal self-hosted SLM (vLLM or HF TGI, GPU on
AKS)." §124–§126 raise data-residency and minimisation concerns with external
inference. What is blocked without this decision: the SLM module cannot be built,
cost/latency models are unquantified, and the data-boundary review (ADR-D6-07) has
no subject. What goes wrong if implicit: a team either over-invests in GPU serving
before product-market fit, or hard-couples to an external API and cannot later meet
the in-tenancy requirement without a rebuild.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Generate language for orchestration/communication (never business truth) | 15.PFF-FA-AI-SLM.md §2, §4, §40 |
| DR-F-02 | Provider-neutral access; swap providers without code change | 15.PFF-FA-AI-SLM.md §6, §15; ADR-D3-14 |
| DR-F-03 | Support fallback across providers/models | 15.PFF-FA-AI-SLM.md §62; ADR-D3-18 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Time-to-first-value | Weeks, not GPU-platform months | 15.PFF-FA-AI-SLM.md §19 |
| DR-N-02 | Data boundary control at scale | In-tenancy inference for sensitive flows | 15.PFF-FA-AI-SLM.md §124–§126; ADR-D6-07 |
| DR-N-03 | Unit cost at volume | Self-host cheaper per token at scale | 15.PFF-FA-AI-SLM.md §103–§105 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Direction fixed: HF first → self-hosted target | Organisational | CLAUDE.md; 15.PFF-FA-AI-SLM.md §5 |
| DR-C-02 | SLM never executes business rules / makes authz | Regulatory/Arch | 15.PFF-FA-AI-SLM.md §4, §40 |
| DR-C-03 | Access only via provider abstraction | Architecture | 15.PFF-FA-AI-SLM.md §6, §15; ADR-D3-14 |
| DR-C-04 | Sensitive data minimised before external inference | Security | 15.PFF-FA-AI-SLM.md §125, §126; ADR-D6-07 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | An open SLM meets quality on PFF-FA tasks | Consider larger/commercial model behind abstraction | SLM eval (15.PFF-FA-AI-SLM.md §92) |
| DR-A-02 | Volume grows enough to justify self-host | Stay on HF longer | Cost model (15.PFF-FA-AI-SLM.md §106) |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Time-to-value (initial) | 18 | Ship the first workflow fast | Setup lead time |
| EC-02 | Data-boundary control | 22 | FA/safeguarding data sensitivity | In-tenancy? minimisation? |
| EC-03 | Quality on PFF-FA tasks | 18 | Must be good enough | Eval scores (15.PFF-FA-AI-SLM.md §97) |
| EC-04 | Unit cost at target volume | 15 | Long-run economics | £/1k workflows (15.PFF-FA-AI-SLM.md §106) |
| EC-05 | Operational burden | 12 | GPU ops are heavy | Team effort/SRE load |
| EC-06 | Portability / no lock-in | 10 | Swap providers freely | Abstraction conformance |
| EC-07 | Scalability & latency control | 5 | Own the tuning knobs later | p95 control |
| | **Total** | **100** | | |

EC-02 = 22 is justified by the safeguarding/PII sensitivity of FA data (15.PFF-FA-AI-SLM.md
§124–§126); it is the criterion most able to override raw convenience.

## 5. Alternatives Considered

### 5.1 Option A — HF Inference API first, self-hosted SLM as target (phased)

**Description.** Ship on HF API behind the abstraction; build self-hosted vLLM/TGI
on AKS GPU as the target; cut over per-workflow when quality/cost/boundary justify.
**Strengths.** Fast start; no early GPU ops; clear path to in-tenancy control and
lower unit cost; matches CLAUDE.md.
**Weaknesses.** Two runtimes to support during transition; requires strict
abstraction discipline.
**Cost / effort.** Low now, medium later (GPU platform).

### 5.2 Option B — Self-hosted SLM from day one

**Description.** Stand up GPU serving immediately.
**Strengths.** In-tenancy from the start; full control.
**Weaknesses.** Heavy GPU ops before product validation; slow time-to-value;
premature capacity/cost commitment (15.PFF-FA-AI-SLM.md §85 warns against premature complexity).
**Cost / effort.** High up-front.

### 5.3 Option C — Commercial hosted LLM API only (e.g. OpenAI/Anthropic/Azure OpenAI)

**Description.** Use a managed commercial LLM as the sole provider.
**Strengths.** Top quality; zero model ops; Azure OpenAI keeps data in Azure region.
**Weaknesses.** Higher per-token cost at volume; external data boundary
(mitigated only partly by Azure OpenAI); lock-in; conflicts with the self-hosted
SLM target and "small model" posture.
**Cost / effort.** Low ops, high recurring; strategic misalignment.

### 5.4 Option D — Azure Machine Learning managed online endpoints (self-host, managed control plane)

**Description.** Self-host the SLM but on Azure ML managed endpoints rather than
raw AKS.
**Strengths.** In-tenancy; less low-level GPU ops than raw AKS; Azure-native.
**Weaknesses.** Still GPU cost/ops; another platform to learn; overlaps ADR-D5-10's
serving-stack decision. Viable as a *how* for the self-host phase, not a different
strategy.
**Cost / effort.** Medium; folded into ADR-D5-10 evaluation.

### 5.5 Option E — Hybrid routing: cheap self-host for common tasks, hosted API for hard tasks

**Description.** Route by task class (15.PFF-FA-AI-SLM.md §56–§60): self-host handles routine
generation, a hosted model handles rare complex cases.
**Strengths.** Cost/quality balance; graceful capability ceiling.
**Weaknesses.** Two providers permanently; more routing/eval/guardrail surface;
premature before either leg is proven.
**Cost / effort.** Medium-high complexity; a later optimisation, not a starting
strategy.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No SLM (rules/templates only) | DR-F-01 — conversational orchestration needs generation |
| Client-side / on-device model | Enterprise server-side architecture (15.PFF-FA-AI-SLM.md §3) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 15.PFF-FA-AI-SLM.md §5, §19–§21, §85,
§103–§106, §124–§126 and the CLAUDE.md direction.

| Criterion | Weight | A: HF→self-host | B: Self-host day 1 | C: Commercial API | D: Azure ML | E: Hybrid |
|---|---|---|---|---|---|---|
| EC-01 Time-to-value | 18 | 5 | 2 | 5 | 3 | 3 |
| EC-02 Data boundary | 22 | 4 | 5 | 2 | 5 | 4 |
| EC-03 Quality | 18 | 4 | 4 | 5 | 4 | 5 |
| EC-04 Unit cost @ volume | 15 | 4 | 5 | 2 | 4 | 5 |
| EC-05 Ops burden | 12 | 4 | 2 | 5 | 3 | 2 |
| EC-06 Portability | 10 | 5 | 4 | 2 | 4 | 4 |
| EC-07 Scale/latency control | 5 | 4 | 5 | 3 | 4 | 5 |
| **Weighted total** | **100** | **432** | **394** | **336** | **407** | **404** |

Totals (×20): **A = 432**, **D = 407**, **E = 404**, **B = 394**, **C = 336**.

**Sensitivity.** A leads D by 25. D and E are the closest; both are really
*implementations of the later phases* of A (D = a way to self-host, per ADR-D5-10;
E = a later cost optimisation). If EC-02 were weighted even higher, B rises but its
time-to-value penalty keeps it behind A. C only wins if quality (EC-03) dominated
everything, which the data-boundary constraint forbids.

## 7. Decision

**PFF AI will adopt the phased strategy: Hugging Face Inference API first, internal
self-hosted SLM (vLLM/TGI on AKS GPU) as the target**, both behind the
provider-neutral abstraction (ADR-D3-14). Cutover is per-workflow, gated on SLM
evaluation (15.PFF-FA-AI-SLM.md §92, §99), cost (§106) and data-boundary review (ADR-D6-07). The
serving-stack (vLLM vs TGI vs Azure ML) is decided separately and remains OPEN in
ADR-D5-10. Hybrid routing (E) is a documented future optimisation, not part of the
initial build. C is rejected for boundary/cost/lock-in; B for premature ops.

**Status rationale.** `Accepted` — the direction is fixed by CLAUDE.md and 15.PFF-FA-AI-SLM.md
§5; this ADR records the alternatives and gates. (The *self-host serving stack* is
the open part and lives in ADR-D5-10 as `Proposed`.)

## 8. Architecture Detail

- **Abstraction** (15.PFF-FA-AI-SLM.md §6, §15; ADR-D3-14): `SLMProvider` protocol with
  provider-neutral request/response contracts (§13–§14); `HuggingFaceProvider` now,
  `SelfHostedProvider` later; no caller imports a provider SDK.
- **Config/secrets** (15.PFF-FA-AI-SLM.md §16–§18): endpoints and `*_secret_ref` via Key Vault
  (ADR-D5-07); per-environment config (§17).
- **Data minimisation** (15.PFF-FA-AI-SLM.md §125–§126; ADR-D6-07): sensitive fields minimised/
  redacted before any external inference call; safeguarding-sensitive flows
  prioritised for early self-host cutover.
- **Fallback** (15.PFF-FA-AI-SLM.md §62–§64; ADR-D3-18): fallback must not be silent; abstraction
  supports provider/model fallback with logged degradation.
- **Cutover**: shadow eval (§157) then canary (§158) per workflow; rollback by
  config (§159).

## 9. Consequences

### 9.1 Positive
- Ship the first workflow without GPU ops; keep a credible path to in-tenancy and
  lower unit cost.
- Provider-agnostic from day one → migration is config, not code.

### 9.2 Negative
- Dual-runtime support window; external inference for sensitive data until
  self-host cutover (mitigated by minimisation + prioritised cutover).

### 9.3 Neutral
- Self-host serving-stack choice deferred to ADR-D5-10.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Immediate in-tenancy inference | Fast time-to-value | AI Arch Lead, DPO |
| Single-runtime simplicity | Optionality + migration path | Platform Eng |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | SLM generates language only; never business truth/authz (15.PFF-FA-AI-SLM.md §4, §40) |
| Precedence chain | SLM output is the lowest tier; never overrides ERC/enterprise |
| Four-state separation | SLM is stateless compute; state lives elsewhere |
| Versioned artefacts | Model + config versioned (ADR-D3-15; 15.PFF-FA-AI-SLM.md §154–§155) |
| Adam persona governs *how*, not *what* | Provider choice is invisible to persona/user |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | External inference exposes sensitive data | Med | High | H | Minimisation/redaction; prioritised self-host (ADR-D6-07) | DPO | Med |
| RSK-02 | HF quality insufficient | Low | Med | M | Model swap behind abstraction; eval gate | ML Eng | Low |
| RSK-03 | Self-host cost/ops overrun | Med | Med | M | Phase gate on cost model (§106); ADR-D5-10 | FinOps | Low |
| RSK-04 | Abstraction leaks provider specifics | Low | High | M | Import-linter + contract tests (ADR-D3-14) | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | SLM eval score on PFF-FA tasks | ≥ gate | < gate | Eval (15.PFF-FA-AI-SLM.md §97, §99) | Every model release |
| QM-02 | p95 generation latency | within budget (ADR-D5-18) | breach | Langfuse | Continuous |
| QM-03 | £ per 1k workflows | tracked vs model | > projection | FinOps (§106) | Monthly |
| QM-04 | % sensitive flows on self-host | rising to 100% | stalled | Config audit | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | External API dependency initially; reduced on self-host |
| Data classification touched | Up to Confidential/Personal — minimised before external calls |
| Personal data / PII | Minimised/redacted pre-inference (15.PFF-FA-AI-SLM.md §126) |
| Children's data and safeguarding | Safeguarding flows prioritised for in-tenancy inference |
| UK GDPR lawful basis and rights impact | Transfer/processing assessed for external provider (ADR-D6-07) |
| Audit and evidential requirements | Provider+model+version on every trace |
| Standards touched | ISO/IEC 42001, 27001, EU AI Act, NIST AI RMF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (initial SLM), 20 (self-host cutover) |
| Repository paths | `src/pff_fa_ai/slm/` |
| Configuration | Provider/endpoint config; secret refs (§16–§18) |
| Contracts / schemas | SLM request/response contracts (§13–§14) |
| Migration | Per-workflow shadow→canary→cutover |
| Dependencies on other ADRs | ADR-D3-14, ADR-D5-10, ADR-D5-11, ADR-D6-07 |
| Effort estimate | M now, L for self-host |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No caller imports a provider SDK directly | Import-linter (ADR-D2-01) |
| AC-02 | Provider swap requires no domain code change | Contract test with two providers |
| AC-03 | Sensitive fields minimised before external call | Data-flow test (ADR-D6-07) |
| AC-04 | Fallback is logged, never silent | Test (15.PFF-FA-AI-SLM.md §64) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Latency/error/cost per provider; Langfuse spans (§131) |
| Alerting | Provider outage, latency breach, error spike |
| Runbook | `docs/runbooks/slm.md` |
| Failure mode and degradation | Provider down → fallback → degraded mode (15.PFF-FA-AI-SLM.md §163, §168) |
| Rollback | Config revert to prior provider/model |
| Support model impact | ML platform team; SRE for self-host phase |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| HF Inference API | setup | usage-based | 15.PFF-FA-AI-SLM.md §104 |
| Self-hosted GPU (later) | platform build | GPU node hours | 15.PFF-FA-AI-SLM.md §105; ADR-D5-11 |
| Abstraction + eval harness | M | low | Shared tooling |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | HF cost exceeds self-host break-even | QM-03 | Accelerate self-host cutover |
| RT-02 | Data-boundary policy tightens | Governance | Move remaining flows in-tenancy |
| RT-03 | Quality gate failing on open models | QM-01 | Reconsider hybrid/commercial behind abstraction |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 SLM |
| Specification sections | 15.PFF-FA-AI-SLM.md §2–§5, §19–§21, §85, §103–§106, §124–§126 |
| Requirement IDs | SLM-STRAT-* |
| Build phases | 6, 20 |
| Code paths | `src/pff_fa_ai/slm/` |
| Configuration | provider/endpoint config |
| Tests | provider contract + data-flow suites |
| Upstream ADRs | ADR-D3-14 |
| Downstream ADRs | ADR-D5-10, ADR-D3-18 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
