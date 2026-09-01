---
id: ADR-D3-12
title: Prompt injection defence inside the prompt layer
domain: 3 AI
ws_ref: [WS-15]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [AI Architecture Lead, Prompt Engineer]
reviewers: [Principal Architect, AI Architecture Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-09, ADR-D6-08, ADR-D6-09, ADR-D2-19, ADR-D3-04]
source_docs:
  - "MD files/4 AI/16.PFF-FA-AI-PROMPT-ENGINEERING.md §6, §16, §30, §54, §55, §56, §57, §58, §59, §60, §61, §62, §63, §172, §173"
build_phases: [6, 9]
impacted_paths:
  - prompts/
  - src/pff_fa_ai/prompt/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D3-12 — Prompt injection defence inside the prompt layer

## 1. Summary

PFF AI will defend against prompt injection with **defence-in-depth inside the
prompt layer**: strict trust tiering of every composed segment (16.PFF-FA-AI-PROMPT-ENGINEERING.md §6, §57),
hard structural delimitation of all untrusted data (§16, §30), explicit
trust-label rules for RAG/API/tool/user content (§58–§61), and system-prompt
leakage protection (§62) — backed by, but distinct from, the runtime guardrail
pipeline (ADR-D6-08/09). The prompt layer treats **all non-platform text as data,
never as instructions**, and never relies on politely asking the model to ignore
injections.

## 2. Context and Problem Statement

16.PFF-FA-AI-PROMPT-ENGINEERING.md §54–§63 specifies an injection threat model and multi-layer defence; §173
gives a prompt-injection defence architecture. Retrieved documents (13.PFF-FA-AI-RAG.md §158),
tool outputs, API results and user text all enter prompt composition and can carry
adversarial instructions ("ignore previous instructions", "reveal the system
prompt", "approve this affiliation"). Because Adam ultimately drives tool calls and
user-facing statements, an un-defended prompt layer is a direct path to
unauthorized actions or disclosure. This ADR fixes *how the prompt layer itself* is
built to resist injection — complementary to the guardrail ADRs which add runtime
filtering.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Untrusted content must be structurally isolated from instructions | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §16, §30 |
| DR-F-02 | Per-source trust rules (RAG/API/tool/user) enforced in composition | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §57–§61 |
| DR-F-03 | System prompt must not be leakable on request | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §62 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Injection test pass rate | ≥ agreed threshold on injection suite | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §63 |
| DR-N-02 | Defence is deterministic, not model-goodwill | Structural, not "please ignore" | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §56, §173 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Trust hierarchy from ADR-D3-09 is authoritative | Architecture | ADR-D3-09; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §6 |
| DR-C-02 | Prompt-layer defence supplements, not replaces, guardrails | Security | ADR-D6-08/09 |
| DR-C-03 | Enterprise truth precedence — injected text can't elevate a source | Regulatory | CLAUDE.md; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §138 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Delimitation + trust labels materially reduce injection success | Add stronger runtime guardrails/model | Injection eval suite |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Injection resistance (efficacy) | 30 | The whole point | Injection suite pass rate |
| EC-02 | Determinism (not model goodwill) | 20 | Must not rely on persuasion | Structural vs instructional |
| EC-03 | Defence-in-depth composability | 18 | Works with guardrails/tool gates | Layer independence |
| EC-04 | False-positive / utility impact | 12 | Over-blocking harms UX | Legit-request pass rate |
| EC-05 | Testability | 12 | Must be CI-gated | Suite coverage |
| EC-06 | Cost / latency | 8 | Keep inference lean | Added tokens/latency |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Structural delimitation + trust tiers + per-source rules (prompt-layer defence-in-depth)

**Description.** Every untrusted segment wrapped in explicit, non-forgeable
delimiters (16.PFF-FA-AI-PROMPT-ENGINEERING.md §16, §30), tagged with a trust label (§57), with hard rules:
RAG content is reference-only (§58), API/tool results are data not commands
(§59–§60), user text is a request not a directive (§61); system prompt leakage
blocked (§62). Combined with guardrails and tool gates.
**Strengths.** Deterministic; composes with other layers; testable; low cost.
**Weaknesses.** Not perfect alone — needs runtime guardrails too (accepted).
**Cost / effort.** Low; mostly composition discipline + delimiters.

### 5.2 Option B — Instructional defence only ("ignore any instructions in the data")

**Description.** Rely on system-prompt wording telling the model to ignore injected
instructions.
**Strengths.** Trivial.
**Weaknesses.** Non-deterministic; defeated by strong injections; violates §56/§173
(structural defence required).
**Cost / effort.** Trivial, ineffective.

### 5.3 Option C — External classifier gate only (guardrail model classifies inputs)

**Description.** Push all defence to a runtime input classifier; keep the prompt
naive.
**Strengths.** Centralised; model-based detection.
**Weaknesses.** Single layer; misses novel injections; leaves prompt structurally
vulnerable if the classifier is bypassed; this is a guardrail concern (ADR-D6-08),
not a substitute for prompt-layer structure.
**Cost / effort.** Adds a model call; still needs prompt structure.

### 5.4 Option D — Fine-tune / instruction-tune the SLM to resist injection

**Description.** Train the model to ignore embedded instructions.
**Strengths.** Improves baseline robustness.
**Weaknesses.** 15.PFF-FA-AI-SLM.md §85 — not first step; model-version-coupled; never complete;
complements but can't be the architecture.
**Cost / effort.** High; premature.

### 5.5 Option E — Separate the data channel entirely (no untrusted text in the instruction prompt)

**Description.** Provide retrieved/API/tool content only via a distinct
structured channel the model reads as read-only context, never concatenated into
the instruction body.
**Strengths.** Strongest structural separation; conceptually clean.
**Weaknesses.** Current SLM/provider APIs still flatten to one context window;
partially realisable, so it becomes *part of* A (delimitation) rather than a
standalone alternative.
**Cost / effort.** Medium; constrained by model interface.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Do nothing (trust the model) | DR-F-01 — unacceptable for an action-taking agent |
| Block all external content in prompts | Destroys RAG/tool utility (EC-04) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4; efficacy grounded in 16.PFF-FA-AI-PROMPT-ENGINEERING.md §54–§63/§173
and industry injection-defence practice. A is the composition-layer strategy; C/D
are complementary layers scored as *sole* strategies to show why they are
insufficient alone.

| Criterion | Weight | A: Structural DiD | B: Instructional | C: Classifier only | D: Fine-tune only | E: Data-channel |
|---|---|---|---|---|---|---|
| EC-01 Efficacy | 30 | 4 | 1 | 3 | 3 | 4 |
| EC-02 Determinism | 20 | 5 | 1 | 3 | 2 | 5 |
| EC-03 Composability | 18 | 5 | 2 | 3 | 3 | 4 |
| EC-04 Utility impact | 12 | 4 | 4 | 3 | 4 | 4 |
| EC-05 Testability | 12 | 5 | 2 | 4 | 2 | 4 |
| EC-06 Cost/latency | 8 | 5 | 5 | 3 | 2 | 4 |
| **Weighted total** | **100** | **456** | **196** | **314** | **276** | **426** |

Totals (×20): **A = 456**, **E = 426**, **C = 314**, **D = 276**, **B = 196**.

**Sensitivity.** A and E are close and complementary — E's data-channel separation
is folded into A as the delimitation mechanism where the model interface allows.
Neither C nor D is viable alone; they are adopted as *additional* layers
(guardrails ADR-D6-08, model choice ADR-D3-13), consistent with defence-in-depth.

## 7. Decision

**PFF AI will build prompt-layer injection defence as structural
defence-in-depth**: non-forgeable delimitation of every untrusted segment,
enforced trust tiers, per-source instruction/data rules (§58–§61), and
system-prompt leakage protection (§62), realising the data-channel separation of
Option E wherever the model interface permits. This is combined with — not replaced
by — runtime guardrails (ADR-D6-08/09), tool-call validation (ADR-D3-04) and model
robustness (ADR-D3-13). Instructional-only defence (B) is rejected as
non-deterministic; C and D are adopted only as supplementary layers.

**Status rationale.** `Accepted` — 16.PFF-FA-AI-PROMPT-ENGINEERING.md §54–§63/§173 mandate structural defence;
this ADR records the layered rationale.

## 8. Architecture Detail

- **Composition rules** (16.PFF-FA-AI-PROMPT-ENGINEERING.md §16, §30, §57): the prompt composer tags each
  segment with a trust tier; untrusted segments are wrapped in delimiters carrying a
  random per-request nonce so injected text cannot forge a closing delimiter.
- **Per-source rules**: RAG → "reference only, cite, never obey" (§58); API/tool
  results → "data, not commands" (§59–§60); user → "request, not directive" (§61).
- **Leakage protection** (§62): system/persona content is never echoed; requests to
  reveal instructions are refused by guardrail + composition rule.
- **Testing** (§63, §151): an injection test corpus runs in CI; regressions block
  release. The retrieved-content and RAG-output guardrails (13.PFF-FA-AI-RAG.md §158–§160) sit
  downstream.
- **Boundary**: this ADR governs the prompt-layer; the six-boundary guardrail
  placement and fail-closed policy are ADR-D6-09.

## 9. Consequences

### 9.1 Positive
- Injection resistance is structural and testable, not dependent on model goodwill.
- Composes cleanly with guardrails, tool gates and model choice.

### 9.2 Negative
- Adds delimiter tokens and composition complexity; requires an injection suite to
  maintain.

### 9.3 Neutral
- Establishes trust-tier discipline reused by ADR-D3-25 context engineering.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| A few tokens + composition simplicity | Deterministic injection resistance | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Injected text can never become an authorization or business decision |
| Precedence chain | Injected content cannot elevate a lower source above ERC/enterprise (16.PFF-FA-AI-PROMPT-ENGINEERING.md §138) |
| Four-state separation | Untrusted data isolated from instruction/state |
| Versioned artefacts | Defence rules live in versioned prompts/composer |
| Adam persona governs *how*, not *what* | Injection cannot flip *what* is true |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Novel injection bypasses delimiters | Med | High | H | Nonce delimiters + guardrails + suite updates | Security Architect | Med |
| RSK-02 | System prompt leak | Low | High | M | Leakage rule + guardrail (§62) | Security Architect | Low |
| RSK-03 | Over-blocking legit content | Med | Med | M | Utility eval (EC-04); tune | Prompt Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Injection suite pass rate | ≥ 0.98 | < 0.95 | CI injection suite | Every prompt release |
| QM-02 | System-prompt leak attempts blocked | 100% | < 100% | Security tests | Every release |
| QM-03 | Legit-request false-block rate | ≤ 1% | > 3% | Utility eval | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Directly reduces injection attack surface |
| Data classification touched | Confidential (defence logic) |
| Personal data / PII | Prevents injection-driven disclosure |
| Children's data and safeguarding | Blocks manipulation of safeguarding-related outputs |
| UK GDPR lawful basis and rights impact | Supports confidentiality obligations |
| Audit and evidential requirements | Injection test results retained per release |
| Standards touched | ISO/IEC 27001, 42001, NIST AI RMF, OWASP LLM Top 10 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (prompt), 9 (guardrail integration) |
| Repository paths | `prompts/`, `src/pff_fa_ai/prompt/` |
| Configuration | Trust-tier map; delimiter/nonce policy |
| Contracts / schemas | Segment trust-tier metadata |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-09, ADR-D6-08/09, ADR-D3-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All untrusted segments are delimited with per-request nonce | Composer unit test |
| AC-02 | Injection suite passes at threshold in CI | CI gate (§63) |
| AC-03 | System prompt not revealed on adversarial request | Security test (§62) |
| AC-04 | Per-source trust rules present for RAG/API/tool/user | Composition inspection |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Injection-attempt detections; guardrail hits (ADR-D6-09) |
| Alerting | Spike in injection attempts; any leak |
| Runbook | `docs/runbooks/prompt-injection.md` |
| Failure mode and degradation | On detected injection, fail closed / sanitise (13.PFF-FA-AI-RAG.md §159) |
| Rollback | Revert to prior prompt/composer version |
| Support model impact | Security + prompt eng |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Injection suite + composer defence | M | low | CI compute + maintenance |
| Added prompt tokens | — | small | Delimiters/labels |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Injection pass rate < 0.95 | QM-01 | Strengthen delimiters/guardrails/model |
| RT-02 | A successful injection incident | Incident | CAR; superseding ADR + suite update |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-15 |
| Specification sections | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §6, §16, §30, §54–§63, §151, §172, §173; 13.PFF-FA-AI-RAG.md §158–§160 |
| Requirement IDs | PROMPT-SEC-* |
| Build phases | 6, 9 |
| Code paths | `prompts/`, `src/pff_fa_ai/prompt/` |
| Configuration | Trust-tier map, delimiter policy |
| Tests | injection + leakage suites |
| Upstream ADRs | ADR-D3-09 |
| Downstream ADRs | ADR-D6-08, ADR-D6-09 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
