---
id: ADR-D3-17
title: Structured output strategy and output validation
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Prompt Engineer]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-14, ADR-D3-16, ADR-D3-04, ADR-D3-19, ADR-D2-07]
source_docs:
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §37, §38, §39, §40, §42, §48"
  - "MD files/4 AI/16.PFF-FA-AI-PROMPT-ENGINEERING.md §42, §43, §44"
build_phases: [6]
impacted_paths:
  - src/pff_fa_ai/slm/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-17 — Structured output strategy and output validation

## 1. Summary

Wherever the platform needs machine-consumable output from the SLM (tool arguments,
routing decisions, extraction results, HIL forms), PFF AI will require the output to
conform to an explicit **Pydantic schema**, obtained through the strongest
constraint the provider supports (native structured/JSON mode or tool-call schema),
and will **validate every output against the schema before use** — with a bounded
repair/retry loop on failure, never acceptance of unvalidated text. The SLM never
executes business rules; structured output is data for deterministic code to act on
(15.PFF-FA-AI-SLM.md §37–§40).

## 2. Context and Problem Statement

15.PFF-FA-AI-SLM.md §37–§39 make structured output a principle and require output validation;
§40 states the SLM must not execute business rules; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §42–§44 cover output
schema and instructions. Free-text parsed with regex is brittle and a security risk
(malformed or injected fields). Without a decision, structured needs are met
inconsistently — some call sites JSON-parse hopefully, others rely on prose — and an
invalid model output can flow into a tool call. This ADR fixes how structure is
requested and how outputs are validated.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Machine-consumable outputs conform to a schema | 15.PFF-FA-AI-SLM.md §37–§38; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §43 |
| DR-F-02 | Every structured output validated before use | 15.PFF-FA-AI-SLM.md §39 |
| DR-F-03 | Invalid output handled (repair/retry/fail), never trusted | 15.PFF-FA-AI-SLM.md §39; ADR-D3-04 |
| DR-C-01 | SLM output is data, not a business decision | 15.PFF-FA-AI-SLM.md §40 |
| DR-N-01 | Deterministic (temp 0) generation for structured tasks | ADR-D3-16 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Providers support a usable structured/JSON/tool mode | Fall back to parse+validate+repair | Provider contract tests |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Output validity / schema conformance | 30 | Correctness & safety | Valid-first-try rate |
| EC-02 | Robustness on failure (repair/retry) | 20 | Must degrade safely | Recovery rate |
| EC-03 | Provider portability | 16 | Works across HF/self-host | Parity |
| EC-04 | Security (no unvalidated data flows) | 16 | Injection/malformed defence | Validation coverage |
| EC-05 | Latency/cost | 10 | Retries cost | Extra calls |
| EC-06 | Simplicity | 8 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Provider-native structured/JSON mode → Pydantic validate → bounded repair

**Description.** Use native JSON/structured mode where available; always validate the
result against a Pydantic schema; on failure, run a bounded repair prompt (return the
validation error to the model) then hard-fail if still invalid.
**Strengths.** High valid-first-try; always validated; safe failure; portable
(falls back to parse+validate where no native mode).
**Weaknesses.** Repair adds occasional latency.
**Cost / effort.** Low-medium.

### 5.2 Option B — Tool/function-calling schema as the structuring mechanism

**Description.** Express the target schema as a tool signature; the model "calls" it.
**Strengths.** Strong structure on providers with good tool support; aligns with
ADR-D3-04.
**Weaknesses.** Not all providers/models equal; conflates "produce data" with
"invoke tool"; still needs validation. Best used *for* actual tool args, not all
structured output.
**Cost / effort.** Low where supported.

### 5.3 Option C — Free-text + regex/heuristic parsing

**Description.** Prompt for a format, parse with regex.
**Strengths.** No provider features needed.
**Weaknesses.** Brittle; silent misparses; security risk; poor on nested data.
**Cost / effort.** Low, unreliable.

### 5.4 Option D — Grammar/constrained decoding (e.g. GBNF/regex-constrained sampling)

**Description.** Constrain the decoder so only schema-valid tokens are emitted.
**Strengths.** Near-100% structural validity; no repair needed.
**Weaknesses.** Requires self-hosted serving control (vLLM/TGI features) — not on HF
API initially; couples to serving stack (ADR-D5-10).
**Cost / effort.** Medium; available only in self-host phase.

### 5.5 Option E — Two-pass: generate then a validator/formatter model pass

**Description.** A second model reshapes output to schema.
**Strengths.** Provider-agnostic structuring.
**Weaknesses.** Doubles cost/latency; second pass can introduce errors; still needs
final validation.
**Cost / effort.** High run cost.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Trust model output without validation | DR-F-02/DR-C-01 — unsafe |
| XML/other formats | Pydantic/JSON is the platform standard (CLAUDE.md) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 15.PFF-FA-AI-SLM.md §37–§42 and 16.PFF-FA-AI-PROMPT-ENGINEERING.md
§42–§44. D scored for the self-host phase where it becomes available.

| Criterion | Weight | A: Native+validate+repair | B: Tool schema | C: Regex | D: Constrained decode | E: Two-pass |
|---|---|---|---|---|---|---|
| EC-01 Validity | 30 | 5 | 4 | 2 | 5 | 4 |
| EC-02 Robustness | 20 | 5 | 4 | 2 | 4 | 4 |
| EC-03 Portability | 16 | 5 | 3 | 4 | 2 | 4 |
| EC-04 Security | 16 | 5 | 4 | 2 | 5 | 4 |
| EC-05 Latency/cost | 10 | 4 | 4 | 5 | 5 | 2 |
| EC-06 Simplicity | 8 | 4 | 4 | 4 | 3 | 2 |
| **Weighted total** | **100** | **482** | **384** | **282** | **412** | **372** |

Totals (×20): **A = 482**, **D = 412**, **B = 384**, **E = 372**, **C = 282**.

**Sensitivity.** A wins now; **D (constrained decoding) becomes the strongest option
once self-hosting lands** (RT-01) and can be layered under A to raise valid-first-try
toward 100% while keeping validation. B is adopted specifically for tool arguments
(ADR-D3-04), which is its natural fit.

## 7. Decision

**PFF AI will require Pydantic-schema-conformant structured output, obtained via the
strongest provider-supported constraint, and will validate every structured output
before use, with a bounded repair/retry then hard-fail (Option A).** Tool arguments
use the tool-call schema mechanism (Option B, per ADR-D3-04). When self-hosting
lands, grammar-constrained decoding (Option D) will be layered beneath A to maximise
first-try validity. Regex parsing (C) and unvalidated trust are forbidden; two-pass
(E) rejected on cost. Validated output is data for deterministic code — the SLM never
executes business rules (15.PFF-FA-AI-SLM.md §40).

**Status rationale.** `Accepted` — 15.PFF-FA-AI-SLM.md §37–§40 mandate structure+validation.

## 8. Architecture Detail

- `generate_structured(req, schema)` on the SLM abstraction (ADR-D3-14): requests
  native structured mode; parses; validates against the Pydantic `schema`.
- On `ValidationError`: one bounded repair attempt feeding the error back; on second
  failure raise `ModelError` (fail closed) — the caller handles per ADR-D3-04/D3-08.
- Structured tasks pinned to temperature 0 (ADR-D3-16); streaming disabled for
  structured output unless the provider supports valid streamed structure (15.PFF-FA-AI-SLM.md
  §48; ADR-D3-19).
- Schemas are the internal-state TypedDicts' boundary Pydantic models (ADR-D2-07).

## 9. Consequences

### 9.1 Positive
- No unvalidated model output ever reaches a tool or business path.
- Portable now; upgradeable to constrained decoding later.
### 9.2 Negative
- Occasional repair latency; schema maintenance.
### 9.3 Neutral
- Reinforces the SLM-as-data-source posture.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Occasional extra repair call | Guaranteed validated output | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Structured output is data; deterministic code decides/executes |
| Precedence chain | Validated output still ranks below ERC/enterprise truth |
| Four-state separation | Output validated at boundary into typed state (ADR-D2-07) |
| Versioned artefacts | Schemas versioned with prompts/models |
| Adam persona governs *how*, not *what* | Structured data path is separate from persona narration |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Model repeatedly emits invalid structure | Med | Med | M | Bounded repair then fail closed; eval | ML Eng | Low |
| RSK-02 | Injected/malformed field reaches tool | Low | High | M | Schema validation + tool gate (ADR-D3-04) | Security Architect | Low |
| RSK-03 | Repair loop inflates latency/cost | Low | Med | M | Bound to 1 retry; monitor | ML Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Valid-first-try rate | ≥ 0.95 | < 0.9 | Langfuse/eval | Per release |
| QM-02 | Post-repair validity | ≥ 0.99 | < 0.97 | Eval | Per release |
| QM-03 | Unvalidated outputs reaching tools | 0 | > 0 | Security tests | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Validation blocks malformed/injected data flows |
| Data classification touched | Internal |
| Personal data / PII | Schema constrains fields; no free-text leakage into tools |
| Children's data and safeguarding | Structured extraction reduces mishandling risk |
| UK GDPR lawful basis and rights impact | Minimises unexpected data propagation |
| Audit and evidential requirements | Validation results traceable |
| Standards touched | ISO/IEC 27001, 42001, OWASP LLM |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 |
| Repository paths | `src/pff_fa_ai/slm/` |
| Configuration | Structured-mode capability flags (registry) |
| Contracts / schemas | Pydantic output schemas |
| Migration | Add constrained decoding at self-host phase |
| Dependencies on other ADRs | ADR-D3-14, ADR-D3-16, ADR-D3-04, ADR-D2-07 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Every structured output validated before use | Code path audit + tests |
| AC-02 | Invalid output triggers bounded repair then fail | Unit test |
| AC-03 | No regex-only parsing of model output remains | Lint/review |
| AC-04 | Tool args validated via schema + gate | Integration test (ADR-D3-04) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Valid-first-try, repair rate, validation failures |
| Alerting | Validity below threshold; repair spikes |
| Runbook | `docs/runbooks/slm.md` |
| Failure mode and degradation | Persistent invalid → fail closed, user-safe message (ADR-D3-08) |
| Rollback | Revert schema/prompt version |
| Support model impact | ML platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Structured pipeline + schemas | M | low | Build |
| Repair retries | — | small | ~5% of structured calls |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Self-hosting available | ADR-D5-10 | Layer constrained decoding (Option D) |
| RT-02 | Valid-first-try < 0.9 | QM-01 | Improve prompt/schema or model |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 |
| Specification sections | 15.PFF-FA-AI-SLM.md §37–§42, §48; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §42–§44 |
| Requirement IDs | SLM-STRUCT-* |
| Build phases | 6 |
| Code paths | `src/pff_fa_ai/slm/` |
| Configuration | registry capability flags |
| Tests | structured-output + validation suites |
| Upstream ADRs | ADR-D3-14, ADR-D3-16 |
| Downstream ADRs | ADR-D3-04, ADR-D3-19 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
