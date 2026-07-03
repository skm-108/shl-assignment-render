from __future__ import annotations

from pathlib import Path
import unittest

from app.catalog import CatalogLoader, CatalogPreprocessor
from app.retrieval.bm25 import BM25Index


class BM25IndexTests(unittest.TestCase):
    def test_contact_center_query_ranks_contact_center_products_first(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "New folder" / "shl_product_catalog.json"
        items = CatalogLoader(catalog_path).load()
        prepared = CatalogPreprocessor().prepare(items)
        index = BM25Index.from_pairs(prepared.search_documents.items())

        hits = index.score("contact center call simulation")

        self.assertGreater(len(hits), 0)
        self.assertIn("contact center", hits[0].text.lower())


if __name__ == "__main__":
    unittest.main()