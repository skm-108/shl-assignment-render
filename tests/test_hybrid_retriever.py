from __future__ import annotations

from pathlib import Path
import unittest

from app.catalog import CatalogLoader, CatalogPreprocessor
from app.retrieval.hybrid import HybridRetriever


class HybridRetrieverTests(unittest.TestCase):
    def test_hybrid_retriever_returns_relevant_contact_center_item(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "New folder" / "shl_product_catalog.json"
        items = CatalogLoader(catalog_path).load()
        prepared = CatalogPreprocessor().prepare(items)

        hits = HybridRetriever().retrieve("contact center call simulation", prepared, top_k=5)

        self.assertGreater(len(hits), 0)
        self.assertIn("contact center", prepared.items_by_id[hits[0].item_id].name.lower())


if __name__ == "__main__":
    unittest.main()