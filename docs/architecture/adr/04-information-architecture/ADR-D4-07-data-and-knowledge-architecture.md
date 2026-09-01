---
id: ADR-D4-07
title: Data and knowledge architecture — domains, classification and ownership
domain: 4 Information
ws_ref: [WS-20]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Data Protection Officer, AI Architecture Lead, Security Architect]
reviewers: [AI Architecture Lead, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-01, ADR-D3-20, ADR-D6-06, ADR-D6-16, ADR-D4-11, ADR-D4-12]
source_docs:
  - "MD files/1 Foundation/5. PFF-FA-AI-STATE-MODEL.md §56"
  - "MD files/3 Context & Integration/9 PFF-FA-AI-MEMORY-CACHE.md §5, §32, §76, §77, §78"
  - "MD files/4 AI/13.PFF-FA-AI-RAG.md §10, §28, §31, §32, §39"
  - "MD files/5 QualityGovernance/20.PFF-FA-AI-GOVERNANCE.md"
build_phases: [3, 8]
impacted_paths:
  - src/pff_fa_ai/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-07 — Data and knowledge architecture — domains, classification and ownership

## 1. Summary

PFF AI will organise all data it touches into explicit **data domains** (enterprise
business data, ERC reference data, conversation/session/memory data, knowledge/RAG
data, operational telemetry), each with a **classification** (Public / Internal /
Confidential / Personal / Special-category) and an **owner**, and will apply
handling rules (retention, access, minimisation) by classification — never mixing a
higher-classification datum into a lower-controlled store. Enterprise business data is
owned by PFF and only referenced; the AI platform owns only its derived/operational
data (5. PFF-FA-AI-STATE-MODEL.md §56; 9 PFF-FA-AI-MEMORY-CACHE.md §5, §32, §76–§78; 13.PFF-FA-AI-RAG.md §10, §31–§32).

## 2. Context and Problem Statement

Data classification and ownership appear across the spec — 5. PFF-FA-AI-STATE-MODEL.md §56 (state security
classification), 9 PFF-FA-AI-MEMORY-CACHE.md §32/§76–§78 (memory retention and cross-user/club isolation),
13.PFF-FA-AI-RAG.md §10/§31–§32/§39 (RAG source authority, business/security metadata, document
classification), 20.PFF-FA-AI-GOVERNANCE.md (governance). But there is no single ADR that names the data
domains, their classifications and owners. Without it, classification is applied
inconsistently per component, retention and access controls diverge, and
special-category/children's data (pervasive in FA football data) can end up in a
store never designed to protect it. This ADR establishes the data map the rest of the
architecture references.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Every datum has a domain, classification and owner | 5. PFF-FA-AI-STATE-MODEL.md §56; 20.PFF-FA-AI-GOVERNANCE.md |
| DR-F-02 | Handling rules (retention/access/minimisation) by classification | 9 PFF-FA-AI-MEMORY-CACHE.md §32; 6 PFF-FA-AI-CONVERSATION-SESSION.md §58–§59 |
| DR-C-01 | Enterprise business data owned by PFF; AI only references | 5. PFF-FA-AI-STATE-MODEL.md §5; ADR-D4-01 |
| DR-C-02 | Cross-user/club isolation | 9 PFF-FA-AI-MEMORY-CACHE.md §77–§78 |
| DR-C-03 | Children's/special-category data specially protected | ADR-D6-16 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Five classification bands suffice | Add bands | DPO review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Compliance & safeguarding fit | 30 | FA/children's data; UK GDPR | DPIA fit |
| EC-02 | Enforceability | 24 | Classification must drive controls | Tag→control mapping |
| EC-03 | Clarity of ownership | 18 | Accountability | Owner per domain |
| EC-04 | Simplicity/usability | 16 | Teams apply it | # bands/domains |
| EC-05 | Extensibility | 12 | New data types | Add domain easily |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Explicit data domains + 5-band classification + named owners + classification-driven controls

**Description.** Enumerate data domains; classify each dataset into Public/Internal/
Confidential/Personal/Special-category; assign an owner; bind retention/access/
minimisation rules to the classification; tag stores accordingly.
**Strengths.** Compliance-fit; enforceable; clear ownership; extensible.
**Weaknesses.** Upfront classification effort.
**Cost / effort.** Medium.

### 5.2 Option B — Binary classification (sensitive / non-sensitive)

**Description.** Two bands only.
**Strengths.** Simple.
**Weaknesses.** Too coarse for UK GDPR personal vs special-category (children's data);
can't tune controls; fails safeguarding nuance.
**Cost / effort.** Low; non-compliant.

### 5.3 Option C — Classify by store, not by datum

**Description.** Treat everything in a store at the store's level.
**Strengths.** Easy to reason about a store.
**Weaknesses.** Over- or under-protects individual data; drives copying to wrong
stores; doesn't handle mixed content.
**Cost / effort.** Low; imprecise.

### 5.4 Option D — Adopt an external data-catalogue/governance tool as the authority

**Description.** Use a data-catalog product to hold the classification/ownership.
**Strengths.** Rich lineage/discovery.
**Weaknesses.** Heavy for the platform's scope; another system; the *policy* still
needs defining here. Better later at enterprise scale.
**Cost / effort.** High.

### 5.5 Option E — Domains + classification, ownership by convention (no enforced controls)

**Description.** Option A's taxonomy but controls applied ad hoc.
**Strengths.** Lighter than A.
**Weaknesses.** Classification without enforcement drifts; the safeguarding risk
remains.
**Cost / effort.** Low; weak.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No formal classification | EC-01 — UK GDPR/safeguarding non-negotiable |
| Copy enterprise data into AI domains for convenience | ADR-D4-01/DR-C-01 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 5. PFF-FA-AI-STATE-MODEL.md §56, 9 PFF-FA-AI-MEMORY-CACHE.md §32/§76–§78,
13.PFF-FA-AI-RAG.md §31–§32, 20.PFF-FA-AI-GOVERNANCE.md and UK GDPR/safeguarding requirements.

| Criterion | Weight | A: Domains+5-band+owned | B: Binary | C: By store | D: External catalog | E: Taxonomy no-enforce |
|---|---|---|---|---|---|---|
| EC-01 Compliance/safeguarding | 30 | 5 | 2 | 3 | 4 | 3 |
| EC-02 Enforceability | 24 | 5 | 3 | 3 | 4 | 2 |
| EC-03 Ownership clarity | 18 | 5 | 3 | 3 | 4 | 4 |
| EC-04 Simplicity | 16 | 4 | 5 | 4 | 2 | 4 |
| EC-05 Extensibility | 12 | 5 | 3 | 3 | 5 | 4 |
| **Weighted total** | **100** | **488** | **312** | **318** | **388** | **314** |

Totals (×20): **A = 488**, **D = 388**, **C = 318**, **E = 314**, **B = 312**.

**Sensitivity.** A leads by 100. D (external catalog) is the only other strong option
and is a natural *future* addition to hold the same taxonomy at enterprise scale
(RT-01); it does not replace defining the policy here.

## 7. Decision

**PFF AI will define explicit data domains, a five-band classification (Public /
Internal / Confidential / Personal / Special-category), and named owners, with
handling controls (retention, access, minimisation, isolation) bound to the
classification (Option A).** Enterprise business data is owned by PFF and only
referenced (ADR-D4-01); the AI platform owns only derived/operational data.
Special-category and children's data receive the strictest controls (ADR-D6-16).
Binary (B), by-store (C) and unenforced (E) options are rejected; an external catalog
(D) is a future scale option.

**Status rationale.** `Accepted` — 20.PFF-FA-AI-GOVERNANCE.md and UK GDPR govern this; ADR sets the map.

## 8. Architecture Detail

- **Domains**: (1) Enterprise business data (PFF-owned, referenced via ERC); (2) ERC
  reference data; (3) Conversation/session/memory data; (4) Knowledge/RAG data; (5)
  Operational telemetry/audit.
- **Classification bands** applied per dataset; stores tagged with the maximum band
  they may hold; a fitness test prevents writing a higher-band datum to a lower-band
  store (complements ADR-D4-01).
- **Controls by band**: retention/TTL (9 PFF-FA-AI-MEMORY-CACHE.md §32), access (ADR-D6-06), minimisation
  (ADR-D6-07), isolation (9 PFF-FA-AI-MEMORY-CACHE.md §77–§78), audit (ADR-D6-17).
- **Ownership**: each domain has an accountable owner recorded in the register;
  knowledge sources carry authority classification (13.PFF-FA-AI-RAG.md §10).

## 9. Consequences

### 9.1 Positive
- Consistent, enforceable classification and ownership across the platform.
### 9.2 Negative
- Upfront and ongoing classification effort.
### 9.3 Neutral
- Referenced by memory (D4-11), cache (D4-12), security (D6-06/16).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of coarse bands | Compliance + safeguarding fit | DPO |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enterprise data owned by PFF; AI owns only derived data |
| Precedence chain | Domains map to authority (enterprise > ERC > cache > RAG) |
| Four-state separation | Domains align with the four state classes (ADR-D4-01) |
| Versioned artefacts | Classification policy versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Special-category data in wrong store | Low | High | H | Store band tags + fitness test | Security Architect | Low |
| RSK-02 | Inconsistent classification | Med | Med | M | Central policy + review | DPO | Low |
| RSK-03 | Ownership gaps | Low | Med | M | Register requires owner per domain | Principal Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Datasets with domain+class+owner | 100% | < 100% | Data register | Quarterly |
| QM-02 | Higher-band-in-lower-store violations | 0 | > 0 | Fitness test | Per build |
| QM-03 | Retention policy coverage | 100% | < 100% | Config audit | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Classification drives least-privilege controls |
| Data classification touched | Defines the scheme itself |
| Personal data / PII | Personal + special-category bands with strict controls |
| Children's data and safeguarding | Special-category handling (ADR-D6-16) |
| UK GDPR lawful basis and rights impact | Enables minimisation, retention, rights handling |
| Audit and evidential requirements | Ownership + classification auditable |
| Standards touched | ISO/IEC 27001, 42001, ISO 9001, UK GDPR |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 3, 8 |
| Repository paths | Platform-wide; store band tags |
| Configuration | Classification policy; retention rules |
| Contracts / schemas | Store band metadata |
| Migration | Classify existing datasets |
| Dependencies on other ADRs | ADR-D4-01, ADR-D6-06, ADR-D6-16 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Every dataset has domain+class+owner | Data register audit |
| AC-02 | No higher-band datum in lower-band store | Fitness test |
| AC-03 | Controls bound to classification | Config review |
| AC-04 | Special-category handled per ADR-D6-16 | DPIA review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Classification coverage; violation counts |
| Alerting | Band violations |
| Runbook | `docs/runbooks/data-governance.md` |
| Failure mode and degradation | Unclassified data blocked from sensitive stores |
| Rollback | Policy revert |
| Support model impact | DPO + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Classification policy + tags | M | low | Governance effort |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Data estate grows large | Governance | Adopt data catalog (Option D) |
| RT-02 | New special-category data type | DPIA | Extend controls |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-20 Data & Knowledge |
| Specification sections | 5. PFF-FA-AI-STATE-MODEL.md §56; 9 PFF-FA-AI-MEMORY-CACHE.md §5, §32, §76–§78; 13.PFF-FA-AI-RAG.md §10, §28, §31–§32, §39; 20.PFF-FA-AI-GOVERNANCE.md |
| Requirement IDs | DATA-* |
| Build phases | 3, 8 |
| Code paths | platform-wide |
| Configuration | classification policy |
| Tests | classification fitness suite |
| Upstream ADRs | ADR-D4-01 |
| Downstream ADRs | ADR-D6-06, ADR-D6-16, ADR-D4-11, ADR-D4-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
