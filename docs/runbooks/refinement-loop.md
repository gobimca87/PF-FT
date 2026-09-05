# Runtime Quality-Gated Refinement Loop Runbook

**Owner:** ML Platform (thresholds/ladders) · AI Governance (strict-class list) — ADR-D3-28
§16 · **Severity:** usually P3; P2 if a below-bar output is committed without a flag/HIL
(QM-03), P2 if the loop breaches the turn latency budget (QM-02).

Implements **ADR-D3-28**. The loop lives in `src/pff_fa_ai/orchestration/refinement/`
(`QualityRefinementController`) and is driven entirely by `config/base/refinement.yaml`
(+ per-environment overrides, which may only *tighten* the bar).

## What it is

After a candidate output for a quality-sensitive task class, a deterministic controller
scores it (`QualityScorer`); below `quality_threshold` it regenerates with critique and/or
escalates up the configured `escalation_ladder`, bounded by `max_refinement_iterations`.
On exhaustion it takes `on_exhaustion` — `return_best_flagged`, `defer_to_hil`, or
`fail_closed` — and never silently ships a below-bar output. `strict: true` classes raise
the bar, mandate `min_escalations >= 1`, and forbid `return_best_flagged`.

The gate is deterministic (the model produces the score *signal*, code decides —
ADR-D3-05). The loop is pre-commit only: it never re-invokes a tool or re-runs an
enterprise write (ADR-D2-11), and it never raises temperature to mask a miss (ADR-D3-16).

## Diagnostic steps

1. Identify the task class and its resolved policy: `config/base/refinement.yaml` +
   `config/environments/<env>/refinement.yaml`. `enabled: false` ⇒ single-shot, no gate.
2. Read the Langfuse loop spans (ADR-D7-02): per-iteration score, action taken, model
   used, token/cost delta; the committed output records the iteration count and the
   ladder rung that produced it.
3. Loop not engaging on poor output → confirm the class is `enabled` and its
   `dimensions`/`quality_threshold` are set as intended.
4. Loop over-triggering / latency high (QM-02) → the runtime scorer may be miscalibrated
   (RSK-02); prefer deterministic dimensions, reserve judge dimensions for strict mode.
5. Escalation not helping (QM-01 uplift ≤ 0, DR-A-02) → review the ladder; disable it to
   degrade to regenerate-only (Option B).

## Recovery

- **Immediate rollback:** set `enabled: false` for the offending task class (config
  revert) — the loop is opt-in, so this restores single-shot behaviour at once.
- **Below-bar commit without flag/HIL (QM-03, P2):** raise a CAR; verify `on_exhaustion`
  handling and strict-class config; supersede the ADR if a design flaw is found.
- **Latency budget breach:** restrict the class to deterministic scorers and/or narrow
  the enabled classes; never remove the iteration cap.
- Never disable the cap, never let the loop re-run a tool/write, never raise temperature
  to force variation.

## Escalation

ML Platform tunes thresholds/ladders; AI Governance owns the strict-class list and any
change to `min_escalations` / `on_exhaustion` for a governance-critical class.
