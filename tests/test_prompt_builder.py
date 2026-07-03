from __future__ import annotations

import unittest

from app.agent.prompt_builder import PromptBuilder
from app.agent.state_machine import ConversationDecision, ConversationState
from app.catalog import CatalogLoader, CatalogPreprocessor
from app.retrieval.hybrid import HybridCandidate
from pathlib import Path


class PromptBuilderTests(unittest.TestCase):
    def test_prompt_builder_formats_retrieved_candidates(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "New folder" / "shl_product_catalog.json"
        items = CatalogLoader(catalog_path).load()
        prepared = CatalogPreprocessor().prepare(items)
        candidate = HybridCandidate(item_id=items[0].entity_id, score=1.0)

        bundle = PromptBuilder().build(
            ConversationDecision(state=ConversationState.RECOMMEND, reply="Recommend."),
            [candidate],
            prepared,
        )

        self.assertIn("Retrieved SHL catalog candidates", bundle.user_prompt)
        self.assertTrue(bundle.system_prompt)


if __name__ == "__main__":
    unittest.main()