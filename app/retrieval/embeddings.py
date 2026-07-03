from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from app.catalog.preprocessing import PreparedCatalog


@dataclass(slots=True)
class EmbeddingRecord:
    item_id: str
    text: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class EmbeddingConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize_embeddings: bool = True


class EmbeddingBackend(Protocol):
    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        ...


class SentenceTransformerEmbeddingBackend:
    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        self.config = config or EmbeddingConfig()
        self._model = None

    def _ensure_model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - import depends on environment
                raise RuntimeError(
                    "sentence-transformers is required for embedding generation"
                ) from exc
            self._model = SentenceTransformer(self.config.model_name)
        return self._model

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._ensure_model()
        vectors = model.encode(
            list(texts),
            batch_size=self.config.batch_size,
            normalize_embeddings=self.config.normalize_embeddings,
            show_progress_bar=False,
        )
        return [list(vector) for vector in vectors]


def build_embedding_records(prepared_catalog: PreparedCatalog) -> list[EmbeddingRecord]:
    records: list[EmbeddingRecord] = []
    for item in prepared_catalog.items:
        records.append(
            EmbeddingRecord(
                item_id=item.entity_id,
                text=item.search_text,
                metadata={
                    "name": item.name,
                    "product_class": item.product_class,
                    "test_type": item.test_type,
                    "languages": item.languages,
                    "job_levels": item.job_levels,
                },
            )
        )
    return records
