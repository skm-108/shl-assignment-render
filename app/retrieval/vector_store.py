from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from app.retrieval.embeddings import EmbeddingRecord, EmbeddingBackend


@dataclass(slots=True)
class ChromaConfig:
    collection_name: str = "shl_catalog"
    persist_directory: str = "data/chroma"


class ChromaVectorStore:
    def __init__(self, config: ChromaConfig | None = None) -> None:
        self.config = config or ChromaConfig()
        self._client = None
        self._collection = None

    def _ensure_client(self) -> Any:
        if self._client is None:
            try:
                import chromadb
            except ImportError as exc:  # pragma: no cover - depends on environment
                raise RuntimeError("chromadb is required for vector storage") from exc
            self._client = chromadb.PersistentClient(path=self.config.persist_directory)
        return self._client

    def _ensure_collection(self) -> Any:
        if self._collection is None:
            client = self._ensure_client()
            self._collection = client.get_or_create_collection(name=self.config.collection_name)
        return self._collection

    def upsert(self, records: Sequence[EmbeddingRecord], embeddings: Sequence[Sequence[float]]) -> None:
        collection = self._ensure_collection()
        collection.upsert(
            ids=[record.item_id for record in records],
            documents=[record.text for record in records],
            embeddings=[list(vector) for vector in embeddings],
            metadatas=[record.metadata for record in records],
        )

    def query(self, query_text: str, embedder: EmbeddingBackend, top_k: int = 10) -> list[dict[str, Any]]:
        collection = self._ensure_collection()
        query_embedding = embedder.encode([query_text])[0]
        result = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        rows: list[dict[str, Any]] = []
        for item_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            rows.append(
                {
                    "item_id": item_id,
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )
        return rows
