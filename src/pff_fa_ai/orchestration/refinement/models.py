from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.models import RefinementSettings, RefinementTaskClassSettings
from pff_fa_ai.orchestration.refinement.states import OnExhaustionAction, RefinementDecision


class QualityScore(BaseModel):
    """ADR-D3-28 §14 boundary model — a per-dimension quality signal produced by the
    scorer. `overall` is the weakest dimension (a below-bar dimension cannot be masked by
    strong ones), consistent with never collapsing evaluation into a single aggregate
    (doc 21 §67)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension_scores: dict[str, float] = Field(default_factory=dict)

    @property
    def overall(self) -> float:
        if not self.dimension_scores:
            return 1.0
        return min(self.dimension_scores.values())

    def meets(self, threshold: float) -> bool:
        return self.overall >= threshold

    def failing_dimensions(self, threshold: float) -> tuple[str, ...]:
        return tuple(
            dimension
            for dimension, score in sorted(self.dimension_scores.items())
            if score < threshold
        )


class ResolvedRefinementPolicy(BaseModel):
    """ADR-D3-28 §8 — the per-task-class settings after resolution and invariant checks.
    Immutable; behaviour is fully config-driven with no hard-coded thresholds (AC-07)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_class: str
    enabled: bool
    quality_threshold: float = Field(ge=0, le=1)
    dimensions: tuple[str, ...]
    max_refinement_iterations: int = Field(ge=0)
    escalation_ladder: tuple[str, ...]
    min_escalations: int = Field(ge=0)
    on_exhaustion: OnExhaustionAction
    strict: bool


class RefinementOutcome(BaseModel):
    """ADR-D3-28 §8/§15 — the terminal result of the loop. `usable` is the single honest
    signal the caller acts on: a below-bar output is never presented as if it passed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_class: str
    final_text: str | None
    decision: RefinementDecision
    committed: bool = False
    flagged: bool = False
    deferred_to_hil: bool = False
    failed_closed: bool = False
    score: QualityScore
    iterations: int = Field(ge=0)
    escalations: int = Field(ge=0)
    model_used: str

    @property
    def usable(self) -> bool:
        """True only when the output may be shown to the user as-is — a clean commit or an
        explicitly flagged best-effort. A HIL deferral or a fail-closed exhaustion is not
        usable and the caller must degrade honestly (ADR-D3-08)."""
        return self.committed or self.flagged


def resolve_refinement_policy(
    settings: RefinementSettings, *, task_class: str
) -> ResolvedRefinementPolicy:
    """ADR-D3-28 §8 — resolve the per-task-class block (falling back to `default`) and
    enforce the strict-mode and boundedness invariants. A contradictory block is a
    configuration error, never silently repaired."""
    block: RefinementTaskClassSettings = settings.task_classes.get(task_class, settings.default)

    if block.enabled and not block.dimensions:
        raise ConfigurationError(
            f"Refinement task class '{task_class}' is enabled but declares no quality "
            "dimensions to score against"
        )
    if block.min_escalations > len(block.escalation_ladder):
        raise ConfigurationError(
            f"Refinement task class '{task_class}' requires {block.min_escalations} "
            f"escalation(s) but its ladder has only {len(block.escalation_ladder)} rung(s)"
        )
    if block.enabled and block.max_refinement_iterations < block.min_escalations:
        raise ConfigurationError(
            f"Refinement task class '{task_class}' allows {block.max_refinement_iterations} "
            f"iteration(s), too few to reach the required {block.min_escalations} escalation(s)"
        )
    if block.strict:
        if block.on_exhaustion == "return_best_flagged":
            raise ConfigurationError(
                f"Strict refinement task class '{task_class}' must not accept a below-bar "
                "output on exhaustion; set on_exhaustion to defer_to_hil or fail_closed"
            )
        if block.min_escalations < 1:
            raise ConfigurationError(
                f"Strict refinement task class '{task_class}' must mandate at least one "
                "escalation (min_escalations >= 1)"
            )

    return ResolvedRefinementPolicy(
        task_class=task_class,
        enabled=block.enabled,
        quality_threshold=block.quality_threshold,
        dimensions=block.dimensions,
        max_refinement_iterations=block.max_refinement_iterations,
        escalation_ladder=block.escalation_ladder,
        min_escalations=block.min_escalations,
        on_exhaustion=OnExhaustionAction(block.on_exhaustion),
        strict=block.strict,
    )
