from __future__ import annotations

from pathlib import Path
import unittest

from app.catalog import CatalogLoader, CatalogPreprocessor
from app.retrieval.filters import FilterCriteria, MetadataFilter


class MetadataFilterTests(unittest.TestCase):
    def test_language_and_job_level_filters_reduce_catalog(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "New folder" / "shl_product_catalog.json"
        items = CatalogLoader(catalog_path).load()
        prepared = CatalogPreprocessor().prepare(items)

        filtered = MetadataFilter().filter(
            prepared.items,
            FilterCriteria(languages={"English (USA)"}, job_levels={"Entry-Level"}),
        )

        self.assertGreater(len(filtered), 0)
        self.assertTrue(all("english (usa)" in {language.lower() for language in item.languages} for item in filtered))
        self.assertTrue(all("entry-level" in {level.lower() for level in item.job_levels} for item in filtered))


if __name__ == "__main__":
    unittest.main()
