from __future__ import annotations

from dataclasses import dataclass

from app.agent.state_machine import ConversationDecision, ConversationState
from app.catalog.preprocessing import PreparedCatalog
from app.retrieval.hybrid import HybridCandidate


@dataclass(slots=True)
class PromptBundle:
    system_prompt: str
    user_prompt: str


class PromptBuilder:
    def build(self, decision: ConversationDecision, candidates: list[HybridCandidate], catalog: PreparedCatalog) -> PromptBundle:
        if decision.state == ConversationState.CLARIFICATION:
            return PromptBundle(
                system_prompt="Ask one concise clarification question. Stay inside the SHL catalog domain.",
                user_prompt=decision.reply,
            )

        if decision.state == ConversationState.COMPARE:
            return PromptBundle(
                system_prompt="Compare only retrieved SHL catalog items. Do not invent product details.",
                user_prompt=self._format_candidates(candidates, catalog),
            )

        if decision.state == ConversationState.REFUSE:
            return PromptBundle(
                system_prompt="Refuse off-topic or legal requests, but stay helpful about SHL assessment selection.",
                user_prompt=decision.reply,
            )

        return PromptBundle(
            system_prompt="Recommend only retrieved SHL catalog items and keep the response schema exact.",
            user_prompt=self._format_candidates(candidates, catalog),
        )

    @staticmethod
    def _format_candidates(candidates: list[HybridCandidate], catalog: PreparedCatalog) -> str:
        lines = ["Retrieved SHL catalog candidates:"]
        for candidate in candidates:
            item = catalog.items_by_id[candidate.item_id]
            lines.append(f"- {item.name} | {item.test_type or 'unknown'} | {item.url}")
        return "\n".join(lines)
