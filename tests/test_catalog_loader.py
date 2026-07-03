from __future__ import annotations

from pathlib import Path
import unittest

from app.catalog import CatalogLoader, CatalogPreprocessor


class CatalogLoaderTests(unittest.TestCase):
    def test_loader_parses_broken_scrape_and_normalizes_records(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "New folder" / "shl_product_catalog.json"
        items = CatalogLoader(catalog_path).load()
        prepared = CatalogPreprocessor().prepare(items)

        self.assertEqual(377, len(items))
        self.assertTrue(all(item.url.startswith("https://www.shl.com/") for item in items))
        self.assertTrue(any(item.product_class == "report" for item in items))
        self.assertTrue(any(item.test_type == "K" for item in items))
        self.assertTrue(any("Microsoft" in item.name for item in items))
        self.assertIn("occupational personality questionnaire opq32r", prepared.items_by_alias)
        self.assertIn("assessment", prepared.items_by_product_class)
        self.assertTrue(prepared.items_by_family)


if __name__ == "__main__":
    unittest.main()