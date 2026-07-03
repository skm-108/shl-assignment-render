from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.api.main import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())

    def test_chat_endpoint_returns_valid_schema(self) -> None:
        response = self.client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "I need an assessment."}]},
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIn("reply", payload)
        self.assertIn("recommendations", payload)
        self.assertIn("end_of_conversation", payload)
        self.assertEqual([], payload["recommendations"])


if __name__ == "__main__":
    unittest.main()