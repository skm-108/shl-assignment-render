from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.catalog.preprocessing import PreparedCatalog
from app.retrieval.bm25 import BM25Index
from app.retrieval.embeddings import EmbeddingBackend
from app.retrieval.filters import FilterCriteria, MetadataFilter
from app.retrieval.vector_store import ChromaVectorStore


@dataclass(slots=True)
class HybridCandidate:
    item_id: str
    score: float
    bm25_score: float = 0.0
    vector_score: float = 0.0
    metadata: dict[str, Any] | None = None


class HybridRetriever:
    def __init__(
        self,
        metadata_filter: MetadataFilter | None = None,
        vector_store: ChromaVectorStore | None = None,
        embedder: EmbeddingBackend | None = None,
    ) -> None:
        self.metadata_filter = metadata_filter or MetadataFilter()
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(
        self,
        query: str,
        prepared_catalog: PreparedCatalog,
        criteria: FilterCriteria | None = None,
        top_k: int = 10,
    ) -> list[HybridCandidate]:
        filtered_items = self.metadata_filter.filter(prepared_catalog.items, criteria)
        if not filtered_items:
            return []

        bm25_index = BM25Index.from_pairs((item.entity_id, item.search_text) for item in filtered_items)
        bm25_hits = bm25_index.score(query)
        candidate_scores: dict[str, HybridCandidate] = {}

        for hit in bm25_hits:
            candidate_scores[hit.item_id] = HybridCandidate(
                item_id=hit.item_id,
                score=hit.score,
                bm25_score=hit.score,
                metadata={"source": "bm25"},
            )

        if self.vector_store is not None and self.embedder is not None:
            for row in self.vector_store.query(query, self.embedder, top_k=top_k):
                item_id = row["item_id"]
                vector_score = 1.0 / (1.0 + float(row.get("distance", 0.0)))
                current = candidate_scores.get(item_id)
                if current is None:
                    candidate_scores[item_id] = HybridCandidate(
                        item_id=item_id,
                        score=vector_score,
                        vector_score=vector_score,
                        metadata=row.get("metadata", {}),
                    )
                    continue
                current.vector_score = vector_score
                current.score = 0.6 * vector_score + 0.4 * current.bm25_score
                current.metadata = row.get("metadata", current.metadata)

        for candidate in candidate_scores.values():
            if candidate.vector_score == 0.0:
                candidate.score = candidate.bm25_score

        ranked = sorted(candidate_scores.values(), key=lambda candidate: candidate.score, reverse=True)
        return ranked[:top_k]
