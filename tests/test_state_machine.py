from __future__ import annotations

import unittest

from app.agent.state_machine import ConversationState, ConversationStateMachine


class StateMachineTests(unittest.TestCase):
    def test_vague_request_gets_clarification(self) -> None:
        decision = ConversationStateMachine().decide([
            {"role": "user", "content": "I need an assessment."},
        ])

        self.assertEqual(ConversationState.CLARIFICATION, decision.state)

    def test_comparison_request_gets_compare_state(self) -> None:
        decision = ConversationStateMachine().decide([
            {"role": "user", "content": "What is the difference between OPQ and GSA?"},
        ])

        self.assertEqual(ConversationState.COMPARE, decision.state)

    def test_legal_request_gets_refusal_state(self) -> None:
        decision = ConversationStateMachine().decide([
            {"role": "user", "content": "Are we legally required under HIPAA to test all staff?"},
        ])

        self.assertEqual(ConversationState.REFUSE, decision.state)

    def test_role_description_can_trigger_recommendation(self) -> None:
        decision = ConversationStateMachine().decide([
            {"role": "user", "content": "Hiring a senior Java developer who works with stakeholders and owns backend services."},
        ])

        self.assertEqual(ConversationState.RECOMMEND, decision.state)


if __name__ == "__main__":
    unittest.main()
