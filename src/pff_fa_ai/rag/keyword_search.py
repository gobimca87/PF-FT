from __future__ import annotations

import re
from typing import Protocol

from pff_fa_ai.rag.models import Chunk

_WORD_PATTERN = re.compile(r"\w+")


def _tokenize(text: str) -> set[str]:
    return {match.group().lower() for match in _WORD_PATTERN.finditer(text)}


class KeywordSearch(Protocol):
    """Doc 13 §52-53 keyword retrieval leg of hybrid search.

    No enterprise keyword/search-engine technology is chosen yet (docs/adr/0003 leaves
    the vector/search store open); this term-overlap scorer is an honest, genuinely
    working placeholder — not a stand-in claiming to be BM25 or a real search engine.
    """

    async def search(
        self, query_text: str, *, tenant_id: str, top_k: int
    ) -> list[tuple[Chunk, float]]: ...


class TermOverlapKeywordSearch:
    def __init__(self) -> None:
        self._corpus: list[Chunk] = []

    async def index(self, chunk: Chunk) -> None:
        self._corpus.append(chunk)

    async def search(
        self, query_text: str, *, tenant_id: str, top_k: int
    ) -> list[tuple[Chunk, float]]:
        query_terms = _tokenize(query_text)
        if not query_terms:
            return []
        scored = []
        for chunk in self._corpus:
            if chunk.tenant_id != tenant_id:
                continue
            overlap = query_terms & _tokenize(chunk.content)
            if overlap:
                scored.append((chunk, len(overlap) / len(query_terms)))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
