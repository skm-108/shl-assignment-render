from __future__ import annotations

from pathlib import Path
import unittest

from app.catalog import CatalogLoader, CatalogPreprocessor
from app.retrieval.embeddings import build_embedding_records


class EmbeddingRecordTests(unittest.TestCase):
    def test_embedding_records_are_built_from_normalized_search_text(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "New folder" / "shl_product_catalog.json"
        items = CatalogLoader(catalog_path).load()
        prepared = CatalogPreprocessor().prepare(items)
        records = build_embedding_records(prepared)

        self.assertEqual(len(items), len(records))
        self.assertTrue(all(record.text for record in records))
        self.assertTrue(all("product_class" in record.metadata for record in records))


if __name__ == "__main__":
    unittest.main()