from __future__ import annotations

from enum import StrEnum

from pff_fa_ai.prompt_engineering.states import PromptRiskLevel

# doc 20 §15/§18 — the same LOW/MEDIUM/HIGH/CRITICAL classification already governs
# prompt risk (Phase 10); governance risk and risk-register severity use the identical
# scale rather than a fourth near-duplicate enum.
GovernanceRiskLevel = PromptRiskLevel


class AiLifecycleState(StrEnum):
    """doc 20 §11 / DEVELOPMENT-GUIDE Phase 21 — the cross-cutting governance-level
    lifecycle, distinct from any single artifact type's own technical status (e.g.
    `prompt_engineering.PromptStatus`'s DRAFT/REVIEW/TEST/... — that governs a prompt's
    own release process; this governs the AI *capability* as a business/risk artifact,
    for the platform and for each governed artifact per the guide)."""

    IDEA = "IDEA"
    ASSESS = "ASSESS"
    DESIGN = "DESIGN"
    BUILD = "BUILD"
    VALIDATE = "VALIDATE"
    APPROVE = "APPROVE"
    DEPLOY = "DEPLOY"
    MONITOR = "MONITOR"
    REVIEW = "REVIEW"
    CHANGE = "CHANGE"
    RETIRE = "RETIRE"


class GovernedArtifactType(StrEnum):
    """DEVELOPMENT-GUIDE Phase 21: "for the platform and for each governed artifact
    (prompts, models, MCP servers)" — the exact scope named by the phase bullet."""

    PLATFORM = "PLATFORM"
    PROMPT = "PROMPT"
    MODEL = "MODEL"
    MCP_SERVER = "MCP_SERVER"


class Likelihood(StrEnum):
    """doc 20 §16 risk classification factor — no fixed scale given in the doc; a
    standard three-point likelihood scale, distinct from `GovernanceRiskLevel`'s
    four-point severity/impact scale."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskStatus(StrEnum):
    """doc 20 §18 risk register "Status" field / §19 "Risk Treatment" outcomes."""

    OPEN = "OPEN"
    MITIGATING = "MITIGATING"
    MITIGATED = "MITIGATED"
    ACCEPTED = "ACCEPTED"
    CLOSED = "CLOSED"
