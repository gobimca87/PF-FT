---
id: ADR-D8-10
title: Vendor lock-in, portability and exit strategy
domain: 8 Business Value
ws_ref: [WS-37]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [AI Architecture Lead, FinOps, Security Architect]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D8-02, ADR-D3-14, ADR-D4-10, ADR-D3-24, ADR-D7-01]
source_docs:
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §95, §96, §97"
  - "DEVELOPMENT-GUIDE.md §2"
build_phases: [24]
impacted_paths:
  - docs/architecture/adr/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-10 — Vendor lock-in, portability and exit strategy

## 1. Summary

PFF AI will manage lock-in by **abstracting swappable dependencies behind provider-neutral
interfaces, preferring open standards/OSS for the core, and documenting an exit strategy per
major dependency** — while accepting deliberate, valuable Azure-native coupling where it earns
its keep (20.PF-FT-AI-GOVERNANCE.md §95–§97; DEVELOPMENT-GUIDE §2). Portability is engineered where it matters
(SLM, embeddings, vector store, observability), not pursued everywhere at cost.

## 2. Context and Problem Statement

20.PF-FT-AI-GOVERNANCE.md §95–§97 third-party AI governance/provider-change/exit-strategy; DEVELOPMENT-GUIDE §2
deferred choices. The platform depends on Azure PaaS, HF, Langfuse, LangGraph and (proposed)
vector store / SLM serving. Unmanaged, these become lock-in that raises cost and risk. This
ADR fixes the lock-in posture and exit strategy.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Abstract swappable dependencies | ADR-D3-14/D4-10/D3-24 |
| DR-F-02 | Documented exit strategy per major dependency | 20.PF-FT-AI-GOVERNANCE.md §97 |
| DR-C-01 | Accept valuable Azure-native coupling deliberately | ADR-D5-08 |
| DR-N-01 | Prefer open standards/OSS for core | ADR-D8-02 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Abstractions hold across providers | Strengthen seams | Contract tests |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Switchability of key dependencies | 28 | Reduce lock-in risk | Swap cost |
| EC-02 | Exit-readiness (documented + tested) | 22 | Real, not paper | Exit plans |
| EC-03 | Cost/pragmatism (not over-abstracting) | 20 | Value | Abstraction cost |
| EC-04 | Data portability | 16 | Get data out | Export paths |
| EC-05 | Simplicity | 14 | Maintainable | Seams count |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Abstract swappable deps + open standards for core + documented per-dependency exit; accept valuable Azure coupling

**Description.** Provider abstractions for SLM (ADR-D3-14), memory/cache (ADR-D4-10), vector
store (ADR-D3-24), observability via OTel (ADR-D7-01); open standards/OSS for the core
(ADR-D8-02); a documented exit strategy per major dependency (20.PF-FT-AI-GOVERNANCE.md §97); deliberate
Azure-native coupling where it clearly pays (ADR-D5-08).
**Strengths.** Pragmatic, switchable where it matters, exit-ready, cost-aware.
**Weaknesses.** Some coupling remains (accepted).
**Cost / effort.** Low-medium.

### 5.2 Option B — Full cloud-agnostic / avoid all lock-in

**Description.** Abstract everything; no cloud-specific services.
**Strengths.** Max portability.
**Weaknesses.** Forgoes valuable managed Azure services; higher cost/complexity; lowest-common-
denominator.
**Cost / effort.** High.

### 5.3 Option C — Accept lock-in (deepest native integration everywhere)

**Description.** Use every Azure/vendor feature; no abstractions.
**Strengths.** Fastest, richest features.
**Weaknesses.** High switching cost; strategic risk; no exit.
**Cost / effort.** Low now, high exit.

### 5.4 Option D — Multi-cloud active portability (run on 2 clouds)

**Description.** Continuously portable across clouds.
**Strengths.** Ultimate flexibility.
**Weaknesses.** Very high cost/complexity; unwarranted for a single-tenancy FA platform.
**Cost / effort.** Very high.

### 5.5 Option E — A + periodic exit-drills (prove a provider can actually be swapped)

**Description.** Option A with periodic exit/portability drills (e.g. swap SLM provider in a
test env) to prove abstractions and exit plans actually work.
**Strengths.** A + proven (not paper) portability.
**Weaknesses.** Drill effort.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No exit strategy | 20.PF-FT-AI-GOVERNANCE.md §97 |
| Abstract nothing | Strategic lock-in risk |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PF-FT-AI-GOVERNANCE.md §95–§97 and DEVELOPMENT-GUIDE §2.

| Criterion | Weight | A: Pragmatic abstraction | B: Cloud-agnostic | C: Accept lock-in | D: Multi-cloud active | E: A+exit-drills |
|---|---|---|---|---|---|---|
| EC-01 Switchability | 28 | 4 | 5 | 1 | 5 | 5 |
| EC-02 Exit-readiness | 22 | 4 | 4 | 1 | 4 | 5 |
| EC-03 Cost/pragmatism | 20 | 5 | 2 | 4 | 1 | 4 |
| EC-04 Data portability | 16 | 4 | 5 | 2 | 5 | 5 |
| EC-05 Simplicity | 14 | 4 | 2 | 5 | 1 | 3 |
| **Weighted total** | **100** | **420** | **368** | **246** | **336** | **456** |

Totals (×20): **E = 456**, **A = 420**, **B = 368**, **D = 336**, **C = 246**.

**Sensitivity.** E (pragmatic abstraction + periodic exit-drills) wins by proving portability
rather than assuming it, at modest cost. Full cloud-agnostic (B) and multi-cloud (D) over-pay
for portability the platform doesn't need; accept-lock-in (C) is strategically risky.

## 7. Decision

**PFF AI will manage lock-in pragmatically: abstract swappable dependencies (SLM, memory/
cache, vector store, observability) behind provider-neutral interfaces, use open standards/OSS
for the core, document an exit strategy per major dependency, deliberately accept valuable
Azure-native coupling, and run periodic exit-drills to prove portability (Option E).** Full
cloud-agnostic (B), accept-all-lock-in (C) and active multi-cloud (D) are rejected.

## 8. Architecture Detail

- Abstractions: `SLMProvider` (ADR-D3-14), `MemoryStore`/`CacheStore` (ADR-D4-10),
  `VectorStore` (ADR-D3-24), OTel observability (ADR-D7-01); core on open frameworks (ADR-D8-02).
- Per-dependency exit strategy (20.PF-FT-AI-GOVERNANCE.md §97): what it is, switching cost, alternative, data-export
  path, trigger to switch — recorded in `docs/architecture/adr/` / open-decisions where relevant.
- Deliberate Azure coupling (APIM, Key Vault, Service Bus, AKS) documented as accepted trade-offs
  (ADR-D5-08/15/07/D2-16). Periodic exit-drills (e.g. swap SLM/vector provider in test) validate
  the abstractions and plans.

## 9. Consequences

### 9.1 Positive
- Switchable where it matters; proven exit-readiness; cost-pragmatic.
### 9.2 Negative
- Some accepted coupling; drill effort.
### 9.3 Neutral
- Reinforces build/buy (D8-02) and abstraction ADRs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Total portability | Valuable Azure-native leverage + pragmatism | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Portability protects the orchestration layer's independence |
| Precedence chain | N/A |
| Four-state separation | Abstractions preserve boundaries |
| Versioned artefacts | Exit plans versioned |
| Adam persona governs *how*, not *what* | Persona is owned, portable content |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Abstraction leaks → hard to switch | Med | Med | M | Contract tests; exit-drills (E) | AI Arch Lead | Low |
| RSK-02 | Deep coupling on a critical vendor | Low | High | M | Documented exit + alternative | Principal Architect | Med |
| RSK-03 | Data trapped in a provider | Low | High | M | Data-export path per dependency | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Key deps with exit plan | 100% | < 100% | Exit register | Quarterly |
| QM-02 | Exit-drill success | pass | fail | Drills | Annual |
| QM-03 | Provider swap cost (est.) | ≤ target | rising | Architecture review | Annual |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Portability supports moving off a compromised provider |
| Data classification touched | Data-export paths must respect classification |
| Personal data / PII | Export/erasure honoured on exit |
| Children's data and safeguarding | Safeguarding data export controlled |
| UK GDPR lawful basis and rights impact | Exit supports data-portability/erasure |
| Audit and evidential requirements | Exit plans + drills recorded |
| Standards touched | ISO/IEC 42001, 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 24 (strategy) → ongoing |
| Repository paths | `docs/architecture/adr/` (exit plans) |
| Configuration | Provider abstractions |
| Contracts / schemas | Abstraction contracts |
| Migration | Provider swaps via abstractions |
| Dependencies on other ADRs | ADR-D8-02, D3-14, D4-10, D3-24, D7-01 |
| Effort estimate | M (ongoing) |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Key deps abstracted | Architecture review |
| AC-02 | Exit plan per major dependency | Exit register |
| AC-03 | Exit-drill passes | Drill report |
| AC-04 | Data-export path exists per dependency | Review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Dependency health; drill outcomes |
| Alerting | Provider EOL/price/policy changes |
| Runbook | `docs/runbooks/exit-strategy.md` |
| Failure mode and degradation | Provider failure → swap via abstraction |
| Rollback | N/A |
| Support model impact | Architecture governance |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Abstractions (shared with other ADRs) | included | negligible | Already built |
| Exit-drills | — | periodic | Ops time |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Provider price/policy/EOL change | Vendor watch | Execute/refresh exit plan |
| RT-02 | Exit-drill fails | Drill | Strengthen abstraction |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-37 |
| Specification sections | 20.PF-FT-AI-GOVERNANCE.md §95–§97; DEVELOPMENT-GUIDE §2 |
| Requirement IDs | EXIT-* |
| Build phases | 24 → ongoing |
| Code paths | abstractions + exit plans |
| Configuration | provider abstractions |
| Tests | contract + exit-drills |
| Upstream ADRs | ADR-D8-02, D3-14, D4-10, D3-24 |
| Downstream ADRs | — |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
