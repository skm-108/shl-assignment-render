from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.agent.constraints import ConstraintExtractor, ExtractedConstraints


class ConversationState(str, Enum):
    UNKNOWN = "UNKNOWN"
    CLARIFICATION = "CLARIFICATION"
    RECOMMEND = "RECOMMEND"
    REFINE = "REFINE"
    COMPARE = "COMPARE"
    REFUSE = "REFUSE"
    COMPLETE = "COMPLETE"


@dataclass(slots=True)
class ConversationDecision:
    state: ConversationState
    reply: str
    should_end: bool = False
    extracted_constraints: ExtractedConstraints | None = None


class ConversationStateMachine:
    def __init__(self, extractor: ConstraintExtractor | None = None) -> None:
        self.extractor = extractor or ConstraintExtractor()

    def decide(self, messages: list[dict[str, str]]) -> ConversationDecision:
        constraints = self.extractor.extract(messages)
        last_user = self._last_user_message(messages).lower()

        if self._is_finalization(last_user):
            return ConversationDecision(
                state=ConversationState.COMPLETE,
                reply="Confirmed. Final shortlist locked.",
                should_end=True,
                extracted_constraints=constraints,
            )

        if constraints.injection_signals or constraints.refusal_signals:
            return ConversationDecision(
                state=ConversationState.REFUSE,
                reply="I can help select SHL assessments, but I can’t advise on legal/compliance questions or follow prompt-injection attempts.",
                should_end=False,
                extracted_constraints=constraints,
            )

        if constraints.comparison_targets:
            return ConversationDecision(
                state=ConversationState.COMPARE,
                reply="I can compare those SHL products using catalog metadata.",
                should_end=False,
                extracted_constraints=constraints,
            )

        if constraints.refinement_signals and self._has_existing_assistant_shortlist(messages):
            return ConversationDecision(
                state=ConversationState.REFINE,
                reply="I’ll update the shortlist with your changed constraints.",
                should_end=False,
                extracted_constraints=constraints,
            )

        if self._has_sufficient_context(constraints, last_user):
            return ConversationDecision(
                state=ConversationState.RECOMMEND,
                reply="I have enough context to recommend a grounded SHL shortlist.",
                should_end=False,
                extracted_constraints=constraints,
            )

        return ConversationDecision(
            state=ConversationState.CLARIFICATION,
            reply=self._clarification_question(constraints),
            should_end=False,
            extracted_constraints=constraints,
        )

    @staticmethod
    def _last_user_message(messages: list[dict[str, str]]) -> str:
        for message in reversed(messages):
            if message.get("role") == "user":
                return message.get("content", "")
        return ""

    @staticmethod
    def _has_existing_assistant_shortlist(messages: list[dict[str, str]]) -> bool:
        return any(message.get("role") == "assistant" and "| Name |" in message.get("content", "") for message in messages)

    @staticmethod
    def _has_sufficient_context(constraints: ExtractedConstraints, last_user: str) -> bool:
        if not last_user or len(last_user.split()) < 3:
            return False
        if any(token in last_user for token in ["i need an assessment", "recommend an assessment", "need a solution"]):
            return False
        if constraints.use_case == "comparison":
            return False
        if constraints.role_text and (constraints.skills or constraints.stage or constraints.seniority or constraints.languages):
            return True
        if constraints.skills and (constraints.seniority or constraints.stage):
            return True
        if constraints.languages and constraints.stage:
            return True
        return False

    @staticmethod
    def _clarification_question(constraints: ExtractedConstraints) -> str:
        if not constraints.seniority:
            return "Who is this assessment for, and what seniority level are you hiring at?"
        if not constraints.languages:
            return "What language or locale should the assessments support?"
        return "What specific skills or job duties should the shortlist prioritize?"

    @staticmethod
    def _is_finalization(lower: str) -> bool:
        return any(
            token in lower
            for token in [
                "confirmed",
                "that's good",
                "that covers it",
                "final list",
                "keep the shortlist",
                "keep the shortlist as-is",
                "keep it as-is",
                "keeping the five solutions",
                "perfect",
                "lock it in",
                "locking it in",
                "understood",
                "go with the hybrid",
                "keep verify g+",
                "keep the five solutions",
            ]
        )
