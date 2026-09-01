from __future__ import annotations

from enum import StrEnum


class EvaluationStatus(StrEnum):
    """doc 21 §66."""

    PASS = "PASS"  # noqa: S105 -- evaluation outcome, not a credential
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DatasetCategory(StrEnum):
    """doc 21 §13, DEVELOPMENT-GUIDE Phase 16's explicit category list."""

    HAPPY_PATH = "HAPPY_PATH"
    NEGATIVE_PATH = "NEGATIVE_PATH"
    BOUNDARY = "BOUNDARY"
    MISSING_DATA = "MISSING_DATA"
    INVALID_DATA = "INVALID_DATA"
    LARGE_CONTEXT = "LARGE_CONTEXT"
    LARGE_ERC = "LARGE_ERC"
    TOOL_FAILURE = "TOOL_FAILURE"
    API_FAILURE = "API_FAILURE"
    SLM_FAILURE = "SLM_FAILURE"
    RAG_FAILURE = "RAG_FAILURE"
    SECURITY = "SECURITY"
    INJECTION = "INJECTION"
    JAILBREAK = "JAILBREAK"
    REGRESSION = "REGRESSION"
    PERFORMANCE = "PERFORMANCE"


class ScoreDimension(StrEnum):
    """doc 21 §67 — never collapse evaluation into a single aggregate score."""

    QUALITY = "QUALITY"
    SAFETY = "SAFETY"
    SECURITY = "SECURITY"
    GROUNDEDNESS = "GROUNDEDNESS"
    PERFORMANCE = "PERFORMANCE"
    COST = "COST"
    RELIABILITY = "RELIABILITY"


class JudgeDimension(StrEnum):
    """doc 21 §61 — dimensions an LLM judge may evaluate."""

    RELEVANCE = "RELEVANCE"
    CLARITY = "CLARITY"
    COMPLETENESS = "COMPLETENESS"
    GROUNDEDNESS = "GROUNDEDNESS"
    STYLE = "STYLE"


class NonJudgeableDimension(StrEnum):
    """doc 21 §61 — an LLM judge must never be the *sole* evaluator for these."""

    AUTHORIZATION = "AUTHORIZATION"
    SECURITY = "SECURITY"
    EXACT_API_BEHAVIOR = "EXACT_API_BEHAVIOR"
    FINANCIAL_CALCULATIONS = "FINANCIAL_CALCULATIONS"
    DETERMINISTIC_BUSINESS_RULES = "DETERMINISTIC_BUSINESS_RULES"
