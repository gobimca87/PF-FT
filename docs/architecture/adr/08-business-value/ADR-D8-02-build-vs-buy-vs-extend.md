---
id: ADR-D8-02
title: Build vs buy vs extend for the orchestration layer
domain: 8 Business Value
ws_ref: [WS-34]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [AI Architecture Lead, Product Owner, FinOps]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D2-06, ADR-D2-02, ADR-D1-01, ADR-D8-10, ADR-D3-13]
source_docs:
  - "DEVELOPMENT-GUIDE.md §1, §2"
  - "MD files/1 Foundation/1 PFF-FA-AI-ARCHITECTURE.md §2"
  - "MD files/5 QualityGovernance/20.PFF-FA-AI-GOVERNANCE.md §95, §97"
build_phases: [0]
impacted_paths:
  - src/pff_fa_ai/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-02 — Build vs buy vs extend for the orchestration layer

## 1. Summary

PFF AI will **build the orchestration layer in-house on open frameworks (Python/FastAPI +
LangGraph) rather than buy a packaged conversational-AI/agent platform**, because the value
and defensibility are in the enterprise-specific orchestration, the Golden-Rule boundary,
and the ERC/guardrail architecture — none of which a generic product provides — while
**buying/extending commodity components** (SLM via HF, observability via Langfuse, cloud
PaaS) where they are not differentiating (DEVELOPMENT-GUIDE §1–§2; 1 PFF-FA-AI-ARCHITECTURE.md §2).

## 2. Context and Problem Statement

DEVELOPMENT-GUIDE §1–§2 frame PFF AI as an orchestration layer over PFF with a specific
Golden-Rule/ERC/guardrail architecture; 1 PFF-FA-AI-ARCHITECTURE.md §2 the platform's purpose. A packaged
conversational-AI product would impose its own control model, undermining the Golden Rule
and enterprise-truth precedence, and would not know PFF's workflows. Yet building
everything (SLM, observability, cloud) would be wasteful. This ADR fixes the build/buy/
extend split.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Preserve Golden-Rule/ERC control model | CLAUDE.md; 1 PFF-FA-AI-ARCHITECTURE.md §2 |
| DR-F-02 | Enterprise-specific orchestration is the value | DEVELOPMENT-GUIDE §1 |
| DR-C-01 | Buy commodity, build differentiating | FinOps/strategy |
| DR-N-01 | Avoid lock-in on core | ADR-D8-10 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Team can build/operate on open frameworks | Buy more; managed services | Capability review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Control-model fit (Golden Rule/ERC) | 30 | Non-negotiable | Boundary preserved |
| EC-02 | Fit to PFF workflows | 22 | Value | Domain fit |
| EC-03 | Total cost of ownership | 18 | Sustainable | TCO |
| EC-04 | Time-to-value | 16 | Ship first workflow | Lead time |
| EC-05 | Lock-in / portability | 14 | Strategic | Exit cost |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Build orchestration on open frameworks; buy/extend commodity components

**Description.** Build the supervisor/agent/harness/ERC/guardrail/prompt orchestration on
Python/FastAPI + LangGraph (ADR-D2-06); buy commodity (HF SLM ADR-D3-13, Langfuse, Azure
PaaS); extend where a component nearly fits.
**Strengths.** Full control of the value/boundary; commodity leverage; manageable TCO;
low lock-in on core.
**Weaknesses.** Build/operate the core.
**Cost / effort.** Medium.

### 5.2 Option B — Buy a packaged conversational-AI/agent platform

**Description.** Adopt a vendor agent/chatbot platform.
**Strengths.** Fast start; managed.
**Weaknesses.** Imposes its control model (undermines Golden Rule/ERC); poor PFF-workflow
fit; heavy lock-in; enterprise-truth precedence hard to enforce.
**Cost / effort.** Low start, high strategic cost.

### 5.3 Option C — Build everything (incl. SLM, observability, cloud primitives)

**Description.** In-house everything.
**Strengths.** Max control.
**Weaknesses.** Wasteful on commodity; slow; high TCO.
**Cost / effort.** High.

### 5.4 Option D — Low-code/RPA-style platform + custom glue

**Description.** Use a low-code automation platform for workflows.
**Strengths.** Fast simple flows.
**Weaknesses.** Doesn't fit agentic/LLM orchestration or the control model; ceiling hit
fast.
**Cost / effort.** Low start; poor fit.

### 5.5 Option E — Build orchestration + buy commodity + adopt selected OSS building blocks (LangGraph, etc.) with abstraction seams

**Description.** Option A with deliberate abstraction seams (provider abstractions
ADR-D3-14/D4-10, bounded LangGraph adoption ADR-D2-06) so bought/OSS pieces are
replaceable.
**Strengths.** A's control + explicit replaceability (portability, ADR-D8-10).
**Weaknesses.** Abstraction discipline.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Buy platform that owns authorization/decisions | Golden Rule (ADR-D1-02) |
| Build a bespoke SLM from scratch | Wasteful; not differentiating |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by DEVELOPMENT-GUIDE §1–§2 and the
control-model constraints.

| Criterion | Weight | A: Build core+buy commodity | B: Buy platform | C: Build all | D: Low-code | E: A+abstraction seams |
|---|---|---|---|---|---|---|
| EC-01 Control-model fit | 30 | 5 | 1 | 5 | 2 | 5 |
| EC-02 PFF-workflow fit | 22 | 5 | 2 | 5 | 2 | 5 |
| EC-03 TCO | 18 | 4 | 3 | 2 | 4 | 4 |
| EC-04 Time-to-value | 16 | 4 | 5 | 1 | 4 | 4 |
| EC-05 Lock-in | 14 | 4 | 1 | 5 | 2 | 5 |
| **Weighted total** | **100** | **452** | **228** | **384** | **256** | **472** |

Totals (×20): **E = 472**, **A = 452**, **C = 384**, **D = 256**, **B = 228**.

**Sensitivity.** E (build core + buy commodity + explicit abstraction seams) edges A by
making bought/OSS pieces replaceable (portability, ADR-D8-10). Buy-platform (B) fails the
control-model criterion decisively — it would own decisions the Golden Rule reserves for
the enterprise.

## 7. Decision

**PFF AI will build the orchestration layer in-house on open frameworks (Python/FastAPI +
LangGraph), buy/extend commodity components (HF SLM, Langfuse, Azure PaaS), and keep
deliberate abstraction seams so bought/OSS pieces are replaceable (Option E).** Buying a
packaged agent platform (B) is rejected — it would impose a control model incompatible with
the Golden Rule and ERC. Build-everything (C) and low-code (D) are rejected.

## 8. Architecture Detail

- Built in-house: supervisor/routing (ADR-D2-05), agent contract/harness (ADR-D3-03/D2-09),
  ERC (ADR-D2-12/D4-02), guardrails (ADR-D6-09), prompt orchestration (ADR-D3-09) — the
  differentiating value + control model.
- Bought/extended: SLM via HF then self-host (ADR-D3-13), Langfuse (ADR-D7-02), Azure PaaS
  (ADR-D5-08); LangGraph adopted boundedly (ADR-D2-06).
- Abstraction seams (ADR-D3-14, D4-10, D3-24) keep commodity pieces replaceable (exit
  strategy ADR-D8-10).

## 9. Consequences

### 9.1 Positive
- Control of value + boundary; commodity leverage; replaceable dependencies.
### 9.2 Negative
- Build/operate the core.
### 9.3 Neutral
- Frames portability (D8-10) and extensibility (D8-08).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Fast start of a bought platform | Control-model fit + defensible value | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Building the core is what makes the Golden Rule enforceable |
| Precedence chain | Custom ERC/guardrails enforce precedence |
| Four-state separation | Built-in, not vendor-imposed |
| Versioned artefacts | Owned artefacts, versioned |
| Adam persona governs *how*, not *what* | Persona owned, not vendor-canned |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Build capacity insufficient | Med | High | H | Buy more commodity; managed services | Principal Architect | Med |
| RSK-02 | OSS dependency risk (LangGraph) | Low | Med | M | Bounded adoption + seams (ADR-D2-06) | AI Arch Lead | Low |
| RSK-03 | Reinventing commodity | Low | Med | M | Buy-commodity policy | FinOps | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Core control model owned in-house | yes | vendor-owned | Architecture review | Per major change |
| QM-02 | Commodity components replaceable via seams | yes | tight coupling | Architecture fitness | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Owned code auditable; fewer opaque vendor paths |
| Data classification touched | Internal |
| Personal data / PII | Data control retained in-tenancy |
| Children's data and safeguarding | Control model keeps safeguarding decisions enterprise-owned |
| UK GDPR lawful basis and rights impact | Data-control ownership |
| Audit and evidential requirements | Owned code + artefacts auditable |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0 (strategy) → all |
| Repository paths | `src/pff_fa_ai/` |
| Configuration | Provider abstractions |
| Contracts / schemas | Abstraction seams |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D2-06, D3-13, D8-10 |
| Effort estimate | Programme-level |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Core orchestration built in-house | Architecture review |
| AC-02 | Commodity bought/extended, replaceable | Seam audit |
| AC-03 | No vendor owns authorization/decisions | Boundary review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Dependency health; build vs buy TCO |
| Alerting | Vendor-dependency incidents |
| Runbook | `docs/runbooks/` (per component) |
| Failure mode and degradation | Commodity component swappable via seam |
| Rollback | Provider swap |
| Support model impact | AI platform team owns core |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Build core | high | maintenance | Programme |
| Buy commodity | setup | usage | HF/Langfuse/Azure |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Build capacity strained | Delivery metrics | Buy more managed services |
| RT-02 | A commodity becomes differentiating | Strategy | Consider building it |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-34 |
| Specification sections | DEVELOPMENT-GUIDE §1–§2; 1 PFF-FA-AI-ARCHITECTURE.md §2; 20.PFF-FA-AI-GOVERNANCE.md §95, §97 |
| Requirement IDs | BVE-BUILD-* |
| Build phases | 0 → all |
| Code paths | `src/pff_fa_ai/` |
| Configuration | abstraction seams |
| Tests | architecture fitness |
| Upstream ADRs | ADR-D1-01, D2-06 |
| Downstream ADRs | ADR-D8-10, D8-08 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
