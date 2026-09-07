from __future__ import annotations

import re
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.guardrails.models import GuardrailContext, GuardrailResult
from pff_fa_ai.guardrails.states import GuardrailDecision, GuardrailSeverity
from pff_fa_ai.rag.models import Citation

_GUARDRAIL_ID = "output-groundedness"
_GUARDRAIL_VERSION = "1.0.0"

# ADR-D3-22 §91 / ADR-D3-28 / ADR-D1-02 (I-1, I-5): the *deterministic* half of
# groundedness — the extractable, checkable subset. This is NOT free-text semantic
# faithfulness (that is the LLM-as-judge dimension, still mocked per docs/adr/0003). We
# enforce the token classes an author is most likely to fabricate and that can be
# verified without a model: monetary amounts, URLs, and structured reference identifiers
# (invoice numbers and the like). Bare numbers and undelimited dates are deliberately NOT
# extracted — they are ambiguous against ordinary prose and would false-positive on
# legitimate copy (e.g. "5 teams", a "2025/26" season). A caller that needs a date or a
# bare number grounded should place its exact emitted form in `grounded_identifiers`.
_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[£$€]\s?\d[\d,]*(?:\.\d{2})?"),  # monetary amounts, e.g. £1,234.00
    re.compile(r"https?://[^\s)\]]+"),  # URLs
    re.compile(r"\b[A-Z]{2,}[-_]?\d{3,}\b"),  # structured ids, e.g. INV-12345, AFF1234
)


def extract_grounding_tokens(text: str) -> frozenset[str]:
    """The structured tokens this checker holds accountable to evidence. Kept module-level
    so a caller can build an evidence set from the same authoritative values it renders
    into a response, guaranteeing a legitimate answer's tokens are all grounded."""
    tokens: set[str] = set()
    for pattern in _TOKEN_PATTERNS:
        tokens.update(match.strip() for match in pattern.findall(text))
    return frozenset(tokens)


class GroundednessEvidence(BaseModel):
    """The authoritative material a candidate answer must stay faithful to. Every field is
    supplied by the caller from data it already holds authoritatively (enterprise API/ERC
    results, registry-resolved portal links) — the checker never fetches or infers.

    - `grounded_identifiers`: every structured token (amount/URL/reference id) that
      legitimately appears in the answer, in the exact form the answer renders it. A
      caller typically builds this with `extract_grounding_tokens` over its authoritative
      values plus the resolved portal-link URLs.
    - `forbidden_terms`: literals whose presence contradicts authoritative state — e.g.
      the status-enum members *other than* the actual status. Their appearance is a
      faithfulness failure (21.PFF-FA-AI-EVALUATION §22). Matched case-insensitively on a
      word boundary, so status phrasing ("was not approved") never trips a raw-enum term.
    - `citations` / `requires_citation`: for a knowledge/RAG answer, at least one citation
      must be present (ADR-D3-22 mandatory-citation). A transactional status readout sets
      `requires_citation=False`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    grounded_identifiers: frozenset[str] = Field(default_factory=frozenset)
    forbidden_terms: frozenset[str] = Field(default_factory=frozenset)
    citations: tuple[Citation, ...] = Field(default_factory=tuple)
    requires_citation: bool = False


class GroundednessFinding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    reason_code: str
    detail: str


class GroundednessReport(BaseModel):
    """The outcome of a groundedness check. `score` feeds the refinement `groundedness`
    dimension (ADR-D3-28); `decision` feeds the OUTPUT guardrail boundary (ADR-D6-09).
    Any finding is treated as blocking — a fabricated amount, link or reference is never a
    soft warning (ADR-D1-02 I-1/I-5)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    findings: tuple[GroundednessFinding, ...] = Field(default_factory=tuple)

    @property
    def grounded(self) -> bool:
        return not self.findings

    @property
    def score(self) -> float:
        return 1.0 if self.grounded else 0.0

    @property
    def reason_codes(self) -> tuple[str, ...]:
        return tuple(finding.reason_code for finding in self.findings)

    @property
    def decision(self) -> GuardrailDecision:
        return GuardrailDecision.ALLOW if self.grounded else GuardrailDecision.BLOCK


def check_groundedness(*, answer: str, evidence: GroundednessEvidence) -> GroundednessReport:
    """Deterministic groundedness check (ADR-D3-22 §91 / ADR-D3-28). Returns a report whose
    findings are empty when the answer is grounded. Ordered so the most severe fabrication
    (an ungrounded identifier) is reported first."""
    findings: list[GroundednessFinding] = []

    ungrounded = sorted(extract_grounding_tokens(answer) - evidence.grounded_identifiers)
    for token in ungrounded:
        findings.append(
            GroundednessFinding(
                reason_code="GR-OUT-UNGROUNDED-ID",
                detail=f"'{token}' does not appear in the authoritative evidence",
            )
        )

    lowered = answer.lower()
    for term in sorted(evidence.forbidden_terms):
        if re.search(rf"\b{re.escape(term.lower())}\b", lowered):
            findings.append(
                GroundednessFinding(
                    reason_code="GR-OUT-CONTRADICTS-ERC",
                    detail=f"answer asserts '{term}', which contradicts authoritative state",
                )
            )

    if evidence.requires_citation and not evidence.citations:
        findings.append(
            GroundednessFinding(
                reason_code="GR-OUT-MISSING-CITATION",
                detail="a knowledge answer must carry at least one citation",
            )
        )

    return GroundednessReport(findings=tuple(findings))


def build_grounded_identifiers(values: Iterable[str]) -> frozenset[str]:
    """Convenience for a caller assembling evidence: union of the grounding tokens found
    across each authoritative string value (a rendered fee, an invoice number, a resolved
    portal URL). A caller passes the exact strings it will render into the answer."""
    tokens: set[str] = set()
    for value in values:
        tokens.update(extract_grounding_tokens(value))
    return frozenset(tokens)


class GroundednessOutputPolicy:
    """ADR-D6-09 OUTPUT-boundary policy realizing the deterministic groundedness check.
    Fail-closed: a context that carries no `groundedness_evidence` BLOCKs rather than
    waving the response through unverified (doc 18 §98; the OUTPUT boundary must not
    silently pass a candidate whose grounding could not be established)."""

    def __init__(self, *, metadata_key: str = "groundedness_evidence") -> None:
        self._metadata_key = metadata_key

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        evidence = context.metadata.get(self._metadata_key)
        if not isinstance(evidence, GroundednessEvidence):
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                guardrail_id=_GUARDRAIL_ID,
                guardrail_version=_GUARDRAIL_VERSION,
                reason_codes=("GR-OUT-EVIDENCE-MISSING",),
                severity=GuardrailSeverity.CRITICAL,
            )
        report = check_groundedness(answer=context.content or "", evidence=evidence)
        if report.grounded:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                guardrail_id=_GUARDRAIL_ID,
                guardrail_version=_GUARDRAIL_VERSION,
                severity=GuardrailSeverity.INFO,
            )
        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            guardrail_id=_GUARDRAIL_ID,
            guardrail_version=_GUARDRAIL_VERSION,
            reason_codes=report.reason_codes,
            severity=GuardrailSeverity.CRITICAL,
        )
