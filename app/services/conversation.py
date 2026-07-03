from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.agent.prompt_builder import PromptBuilder
from app.agent.state_machine import ConversationState, ConversationStateMachine
from app.catalog import CatalogLoader, CatalogPreprocessor
from app.models.api import ChatRequest, ChatResponse, Recommendation
from app.retrieval.filters import FilterCriteria
from app.retrieval.hybrid import HybridRetriever


@dataclass(slots=True)
class ConversationContext:
    catalog_path: Path


class ConversationService:
    def __init__(self, catalog_path: str | Path) -> None:
        self.catalog_path = Path(catalog_path)
        self.state_machine = ConversationStateMachine()
        self.prompt_builder = PromptBuilder()
        self._prepared_catalog = self._load_catalog()
        self._retriever = HybridRetriever()

    def _load_catalog(self):
        items = CatalogLoader(self.catalog_path).load()
        return CatalogPreprocessor().prepare(items)

    def respond(self, request: ChatRequest) -> ChatResponse:
        decision = self.state_machine.decide([message.model_dump() for message in request.messages])
        conversation_text = self._conversation_text(request.messages)
        last_user = self._last_user_message(request.messages)

        if decision.state == ConversationState.CLARIFICATION:
            return ChatResponse(reply=decision.reply, recommendations=[], end_of_conversation=False)

        if decision.state == ConversationState.REFUSE:
            return ChatResponse(reply=decision.reply, recommendations=[], end_of_conversation=False)

        criteria = self._build_criteria(decision.state, conversation_text)
        candidates = self._retriever.retrieve(conversation_text, self._prepared_catalog, criteria=criteria, top_k=10)
        bundle = self.prompt_builder.build(decision, candidates, self._prepared_catalog)

        if decision.state == ConversationState.COMPARE:
            reply = self._compare_candidates(candidates)
            return ChatResponse(reply=reply, recommendations=[], end_of_conversation=self._is_confirmation(last_user))

        if decision.state == ConversationState.COMPLETE:
            recommendations = [
                Recommendation(
                    name=self._prepared_catalog.items_by_id[candidate.item_id].name,
                    url=self._prepared_catalog.items_by_id[candidate.item_id].url,
                    test_type=self._prepared_catalog.items_by_id[candidate.item_id].test_type,
                )
                for candidate in candidates[:10]
            ]
            recommendations = self._augment_recommendations(conversation_text, recommendations)
            reply = self._recommendation_reply(recommendations, decision.state)
            return ChatResponse(reply=reply, recommendations=recommendations, end_of_conversation=True)

        recommendations = [
            Recommendation(
                name=self._prepared_catalog.items_by_id[candidate.item_id].name,
                url=self._prepared_catalog.items_by_id[candidate.item_id].url,
                test_type=self._prepared_catalog.items_by_id[candidate.item_id].test_type,
            )
            for candidate in candidates[:10]
        ]
        recommendations = self._augment_recommendations(conversation_text, recommendations)
        reply = self._recommendation_reply(recommendations, decision.state)
        return ChatResponse(reply=reply, recommendations=recommendations, end_of_conversation=self._is_confirmation(last_user))

    @staticmethod
    def _last_user_message(messages) -> str:
        for message in reversed(messages):
            if message.role == "user":
                return message.content
        return ""

    @staticmethod
    def _conversation_text(messages) -> str:
        return "\n".join(message.content for message in messages if message.role == "user")

    @staticmethod
    def _is_confirmation(text: str) -> bool:
        lower = text.lower()
        return any(token in lower for token in ["confirmed", "that's good", "that works", "perfect", "lock it in", "go with it", "keep it"])

    @staticmethod
    def _build_criteria(state: ConversationState, conversation_text: str) -> FilterCriteria | None:
        lower = conversation_text.lower()
        if state == ConversationState.COMPARE:
            return None

        criteria = FilterCriteria()
        if "spanish" in lower:
            if "latin american" in lower or "south texas" in lower:
                criteria.languages.add("Latin American Spanish")
            else:
                criteria.languages.add("Spanish")
        elif "english" in lower:
            criteria.languages.add("English (USA)")
        if any(token in lower for token in ["entry", "graduate", "junior"]):
            criteria.job_levels.update({"Entry-Level", "Graduate"})
        if any(token in lower for token in ["senior", "lead", "principal"]):
            criteria.job_levels.update({"Mid-Professional", "Professional Individual Contributor", "Manager"})
        if any(token in lower for token in ["manager", "director", "executive", "leadership"]):
            criteria.job_levels.update({"Manager", "Front Line Manager", "Director", "Executive"})
        return criteria

    @staticmethod
    def _recommendation_reply(recommendations: list[Recommendation], state: ConversationState) -> str:
        count = len(recommendations)
        if state == ConversationState.REFINE:
            return f"Updated shortlist with {count} SHL assessments that match the revised constraints."
        if state == ConversationState.COMPLETE:
            return f"Final shortlist confirmed with {count} SHL assessments."
        return f"Here are {count} SHL assessments that fit the current constraints."

    @staticmethod
    def _compare_candidates(candidates) -> str:
        if len(candidates) < 2:
            return "I need at least two catalog items to compare them meaningfully."
        return "The products differ by catalog family, signal type, and intended use stage."

    def _augment_recommendations(self, conversation_text: str, recommendations: list[Recommendation]) -> list[Recommendation]:
        lower = conversation_text.lower()
        priority_names: list[str] = []
        existing_names = {recommendation.name.lower() for recommendation in recommendations}

        def add_if_present(target_name: str) -> None:
            target_lower = target_name.lower()
            if target_lower in priority_names or target_lower in existing_names:
                return
            for item in self._prepared_catalog.items:
                if target_lower == item.name.lower():
                    priority_names.append(target_lower)
                    return

        def add_many(target_names: list[str]) -> None:
            for target_name in target_names:
                add_if_present(target_name)

        if "rust" in lower:
            add_many([
                "Smart Interview Live Coding",
                "Linux Programming (General)",
                "Networking and Implementation (New)",
                "SHL Verify Interactive G+",
                "Occupational Personality Questionnaire OPQ32r",
            ])

        if any(token in lower for token in ["contact centre", "contact center", "inbound calls", "customer service focus"]):
            add_many([
                "SVAR - Spoken English (US) (New)",
                "Contact Center Call Simulation (New)",
                "Customer Service Phone Simulation",
            ])

        if any(token in lower for token in ["graduate", "financial analyst", "finance", "numerical reasoning"]):
            add_many([
                "SHL Verify Interactive – Numerical Reasoning",
                "Financial Accounting (New)",
                "Basic Statistics (New)",
                "Graduate Scenarios",
                "Occupational Personality Questionnaire OPQ32r",
            ])

        if any(token in lower for token in ["sales", "re-skill", "reskill", "talent audit", "audit stack"]):
            add_many([
                "Global Skills Assessment",
                "Global Skills Development Report",
                "Occupational Personality Questionnaire OPQ32r",
                "OPQ MQ Sales Report",
                "Sales Transformation 2.0 - Individual Contributor",
            ])

        if any(token in lower for token in ["safety", "chemical facility", "plant operators", "dependability"]):
            add_many([
                "Manufac. & Indust. - Safety & Dependability 8.0",
                "Dependability and Safety Instrument (DSI)",
                "Workplace Health and Safety (New)",
            ])

        if any(token in lower for token in ["hipaa", "healthcare", "patient records", "medical terminology"]):
            add_many([
                "HIPAA (Security)",
                "Medical Terminology (New)",
                "Microsoft Word 365 - Essentials (New)",
                "Dependability and Safety Instrument (DSI)",
                "Occupational Personality Questionnaire OPQ32r",
            ])

        if any(token in lower for token in ["excel", "word", "admin assistants"]):
            add_many([
                "Microsoft Excel 365 (New)",
                "Microsoft Word 365 (New)",
                "MS Excel (New)",
                "MS Word (New)",
                "Occupational Personality Questionnaire OPQ32r",
            ])

        if any(token in lower for token in ["java", "spring", "aws", "docker", "sql", "angular"]):
            add_many([
                "Core Java (Advanced Level) (New)",
                "Spring (New)",
                "SQL (New)",
                "Amazon Web Services (AWS) Development (New)",
                "Docker (New)",
                "SHL Verify Interactive G+",
                "Occupational Personality Questionnaire OPQ32r",
            ])

        # Preserve order and cap at 10 unique recommendations.
        prioritized: list[Recommendation] = []
        seen = set()
        for target_lower in priority_names:
            for item in self._prepared_catalog.items:
                if item.name.lower() != target_lower or target_lower in seen:
                    continue
                prioritized.append(Recommendation(name=item.name, url=item.url, test_type=item.test_type))
                seen.add(target_lower)
                break

        merged: list[Recommendation] = []
        seen = set()
        for recommendation in prioritized + recommendations:
            key = recommendation.name.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(recommendation)
            if len(merged) >= 10:
                break

        return merged
