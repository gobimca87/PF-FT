---
id: ADR-D6-08
title: Prompt injection and jailbreak defence architecture
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [AI Architecture Lead, Prompt Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-12, ADR-D6-09, ADR-D3-04, ADR-D6-12, ADR-D2-19]
source_docs:
  - "MD files/4 AI/18.PF-FT-AI-GUARDRAILS.md §16, §17, §18, §19, §20, §21, §22, §23, §24, §25, §26, §28, §29, §30, §31"
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §37, §38, §47"
build_phases: [9]
impacted_paths:
  - src/pf_ft_ai/guardrails/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-08 — Prompt injection and jailbreak defence architecture

## 1. Summary

PFF AI will defend against prompt injection and jailbreaks with **layered runtime
guardrails** covering direct and indirect injection across all untrusted channels —
user input, RAG documents, tool/API results, MCP responses, memory, Service Bus events —
combining structural defences (ADR-D3-12) with detection/classification and fail-closed
handling (doc 18 §16–§31; doc 19 §37–§38, §47). No single technique is trusted alone;
authoritative data always outranks injected instructions.

## 2. Context and Problem Statement

Doc 18 §16–§31 detail injection defence across every channel (direct §17, indirect §18,
detection §20–§21, jailbreak §22–§23, multi-turn §24, memory §25, RAG §26, API §28, tool
§29, MCP §30, Service Bus §31); doc 19 §37–§38/§47 prompt-injection/jailbreak/memory-
injection. ADR-D3-12 covers the *prompt-layer* structural defence; this ADR fixes the
*runtime guardrail* defence architecture that complements it across all channels.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Defend direct + indirect injection on all channels | doc 18 §17–§18, §26–§31 |
| DR-F-02 | Jailbreak + multi-turn defence | doc 18 §22–§24 |
| DR-C-01 | Authoritative data outranks injected instructions | doc 18 §27, §58 |
| DR-F-03 | Fail-closed on detected injection | doc 18 §11, §54 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Layered defence materially reduces success | Add stronger model/guardrails | Injection eval |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Efficacy across all channels | 30 | Coverage | Injection suite |
| EC-02 | Defence-in-depth (no single point) | 22 | Resilience | Layer independence |
| EC-03 | Fail-closed correctness | 18 | Safe on detection | Behaviour |
| EC-04 | False-positive/utility | 14 | UX | Legit pass rate |
| EC-05 | Maintainability (evolving attacks) | 16 | Update cadence | Rule/model updates |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Layered guardrails: structural + detection/classification + per-channel rules + fail-closed

**Description.** Combine ADR-D3-12 structural defence with runtime input/content
guardrails, an injection/jailbreak classifier, per-channel trust rules (RAG/API/tool/
MCP/memory/SB), and fail-closed handling; authoritative-data-priority enforced (§58).
**Strengths.** Broad, resilient, testable, safe on detection.
**Weaknesses.** Multiple layers to maintain vs evolving attacks.
**Cost / effort.** Medium.

### 5.2 Option B — Structural-only (delimiters/trust tiers, no detection)

**Description.** Rely solely on ADR-D3-12 structure.
**Strengths.** Deterministic; cheap.
**Weaknesses.** Misses indirect/novel injections a classifier catches; no runtime
detection.
**Cost / effort.** Low; partial.

### 5.3 Option C — Classifier-only (ML injection detector)

**Description.** One ML detector gates inputs.
**Strengths.** Catches many patterns.
**Weaknesses.** Single point; evadable; no structural backstop.
**Cost / effort.** Medium; brittle alone.

### 5.4 Option D — Model-intrinsic only (rely on a robust instruction-tuned model)

**Description.** Trust the model to resist injection.
**Strengths.** No extra components.
**Weaknesses.** Non-deterministic; model-version-coupled; never complete.
**Cost / effort.** Low; insufficient.

### 5.5 Option E — Layered + human-in-the-loop for high-risk actions

**Description.** Option A plus HIL confirmation before any high-impact action even if
guardrails pass.
**Strengths.** Strongest for irreversible actions.
**Weaknesses.** HIL latency/cost for every high-risk action; use selectively (ties to
ADR-D3-07 confirmation).
**Cost / effort.** Medium; targeted.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| "Please ignore injections" instruction only | doc 18 §19; non-deterministic |
| No defence | Unacceptable for an action-taking agent |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 18 §16–§31 and doc 19 §37–§47.

| Criterion | Weight | A: Layered | B: Structural-only | C: Classifier-only | D: Model-intrinsic | E: Layered+HIL |
|---|---|---|---|---|---|---|
| EC-01 Efficacy | 30 | 5 | 3 | 3 | 2 | 5 |
| EC-02 Defence-in-depth | 22 | 5 | 3 | 2 | 1 | 5 |
| EC-03 Fail-closed | 18 | 5 | 4 | 4 | 2 | 5 |
| EC-04 Utility | 14 | 4 | 5 | 3 | 5 | 3 |
| EC-05 Maintainability | 16 | 4 | 4 | 3 | 3 | 4 |
| **Weighted total** | **100** | **466** | **372** | **298** | **246** | **462** |

Totals (×20): **A = 466**, **E = 462**, **B = 372**, **C = 298**, **D = 246**.

**Sensitivity.** A and E are near-tied; HIL for high-risk actions (E) is adopted
*selectively* (per ADR-D3-07 irreversibility), giving A's breadth plus human oversight
exactly where it matters, without HIL on every turn. Single-technique options (B/C/D)
are insufficient alone.

## 7. Decision

**PFF AI will use layered runtime guardrails — structural defence (ADR-D3-12) +
injection/jailbreak detection/classification + per-channel trust rules across user/RAG/
API/tool/MCP/memory/Service-Bus + fail-closed handling, with authoritative-data-priority
enforced (Option A), and human-in-the-loop confirmation added selectively before
high-risk/irreversible actions (Option E enhancement, per ADR-D3-07).** Single-technique
approaches (B/C/D) are rejected as sole defences.

## 8. Architecture Detail

- Guardrails run at the six boundaries (ADR-D6-09); each untrusted channel has rules
  (RAG §26/§27, API §28, tool §29, MCP §30, memory §25, SB §31); a classifier scores
  injection/jailbreak (§20–§23); multi-turn tracking (§24).
- Detection → fail closed / sanitise (§11, §54); authoritative data priority (§58) means
  injected instructions can never override enterprise/ERC.
- High-risk actions require confirmation (ADR-D3-07) regardless of guardrail pass.
- Injection eval suite in CI (ties to ADR-D3-12 QM-01).

## 9. Consequences

### 9.1 Positive
- Broad, resilient, fail-closed injection defence with targeted human oversight.
### 9.2 Negative
- Multiple layers + classifier to maintain against evolving attacks.
### 9.3 Neutral
- Complements structural prompt-layer defence (D3-12).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some latency/cost of layers | Resilient injection defence | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Injection can never become an action/authz decision |
| Precedence chain | Authoritative data outranks injected instructions (§58) |
| Four-state separation | Untrusted channels isolated from authoritative state |
| Versioned artefacts | Guardrail rules/classifier versioned |
| Adam persona governs *how*, not *what* | Injection cannot change what is true |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Novel injection bypasses layers | Med | High | H | Layered + suite updates + HIL for high-risk | Security Architect | Med |
| RSK-02 | Indirect injection via RAG doc | Med | High | H | RAG content guardrail (§26; ADR-D6-12) | AI Arch Lead | Low |
| RSK-03 | Over-blocking legit input | Med | Med | M | Utility eval; tuned thresholds | Prompt Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Injection suite pass rate | ≥ 0.98 | < 0.95 | CI suite | Per release |
| QM-02 | High-risk actions without confirmation | 0 | > 0 | Tests | Continuous |
| QM-03 | Legit-input false-block rate | ≤ 1% | > 3% | Utility eval | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Major reduction of injection/jailbreak risk |
| Data classification touched | Confidential (defence logic) |
| Personal data / PII | Prevents injection-driven disclosure |
| Children's data and safeguarding | Blocks manipulation of safeguarding outputs |
| UK GDPR lawful basis and rights impact | Supports confidentiality/integrity |
| Audit and evidential requirements | Detections logged |
| Standards touched | ISO/IEC 27001, 42001, OWASP LLM Top 10, NIST AI RMF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 9 |
| Repository paths | `src/pf_ft_ai/guardrails/` |
| Configuration | Rules, classifier, thresholds |
| Contracts / schemas | Guardrail result (doc 18 §10) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-12, D6-09, D3-04, D6-12 |
| Effort estimate | L |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Injection suite passes at threshold | CI |
| AC-02 | Each untrusted channel has guardrail rules | Coverage audit |
| AC-03 | Detection fails closed | Test |
| AC-04 | High-risk actions confirmed | Test (ADR-D3-07) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Injection detections; block rate; classifier drift |
| Alerting | Injection spikes; any successful bypass |
| Runbook | `docs/runbooks/injection.md` |
| Failure mode and degradation | Detected injection → fail closed/sanitise |
| Rollback | Rule/classifier version revert |
| Support model impact | Security + AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Guardrail layers + classifier | L | per-call | Build + inference |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Pass rate < 0.95 | QM-01 | Strengthen layers/model |
| RT-02 | Injection incident | Incident | CAR; update suite + rules |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | doc 18 §16–§31, §54, §58; doc 19 §37–§38, §47 |
| Requirement IDs | SEC-INJ-* |
| Build phases | 9 |
| Code paths | `src/pf_ft_ai/guardrails/` |
| Configuration | rules/classifier |
| Tests | injection/jailbreak suites |
| Upstream ADRs | ADR-D3-12 |
| Downstream ADRs | ADR-D6-09, D6-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
