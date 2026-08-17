from __future__ import annotations

from typing import Protocol

from pf_ft_ai.rag.models import RetrievedChunk


class Reranker(Protocol):
    """Doc 13 §65-67 — reranks candidates; must never invent content, change
    authorization, or modify source text."""

    async def rerank(
        self, query_text: str, candidates: list[RetrievedChunk], *, top_n: int
    ) -> list[RetrievedChunk]: ...


class ScoreTruncationReranker:
    """Orders by the existing fused score and truncates to top_n. No ML reranker model
    has been evaluated/selected yet (doc 13 §67 `model: configured-reranker`) — this is
    the honest baseline until one is."""

    async def rerank(
        self, query_text: str, candidates: list[RetrievedChunk], *, top_n: int
    ) -> list[RetrievedChunk]:
        ordered = sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
        return ordered[:top_n]
