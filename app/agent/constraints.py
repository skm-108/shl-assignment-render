from __future__ import annotations

from dataclasses import dataclass, field
import re


LANGUAGE_PATTERNS = {
    "english": "English (USA)",
    "spanish": "Spanish",
    "french": "French",
    "german": "German",
    "portuguese": "Portuguese",
    "arabic": "Arabic",
    "dutch": "Dutch",
    "italian": "Italian",
    "japanese": "Japanese",
    "korean": "Korean",
    "chinese": "Chinese Simplified",
}

SENIORITY_PATTERNS = [
    (r"entry[- ]level|junior|graduate", "entry-level"),
    (r"mid[- ]level|mid[- ]professional|4 years|5 years", "mid-level"),
    (r"senior|lead|staff|principal", "senior"),
    (r"manager|head|director|executive|cxo", "leadership"),
]


@dataclass(slots=True)
class ExtractedConstraints:
    role_text: str = ""
    seniority: str = ""
    years_of_experience: int | None = None
    languages: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    stage: str = ""
    use_case: str = ""
    comparison_targets: list[str] = field(default_factory=list)
    refinement_signals: list[str] = field(default_factory=list)
    refusal_signals: list[str] = field(default_factory=list)
    injection_signals: list[str] = field(default_factory=list)


class ConstraintExtractor:
    def extract(self, messages: list[dict[str, str]]) -> ExtractedConstraints:
        text = "\n".join(message.get("content", "") for message in messages).strip()
        lower = text.lower()

        constraints = ExtractedConstraints()
        constraints.role_text = self._extract_role_text(text)
        constraints.seniority = self._extract_seniority(lower)
        constraints.years_of_experience = self._extract_years(lower)
        constraints.languages = self._extract_languages(lower)
        constraints.skills = self._extract_skills(lower)
        constraints.stage = self._extract_stage(lower)
        constraints.use_case = self._extract_use_case(lower)
        constraints.comparison_targets = self._extract_comparisons(lower)
        constraints.refinement_signals = self._extract_refinements(lower)
        constraints.refusal_signals = self._extract_refusal_signals(lower)
        constraints.injection_signals = self._extract_injection_signals(lower)
        return constraints

    @staticmethod
    def _extract_role_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        candidate = " ".join(lines)
        if len(candidate) > 180:
            candidate = candidate[:180]
        return candidate

    @staticmethod
    def _extract_seniority(lower: str) -> str:
        for pattern, label in SENIORITY_PATTERNS:
            if re.search(pattern, lower):
                return label
        return ""

    @staticmethod
    def _extract_years(lower: str) -> int | None:
        match = re.search(r"(\d+)\+?\s+years?", lower)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _extract_languages(lower: str) -> list[str]:
        languages: list[str] = []
        for pattern, canonical in LANGUAGE_PATTERNS.items():
            if pattern in lower:
                languages.append(canonical)
        return sorted(dict.fromkeys(languages))

    @staticmethod
    def _extract_skills(lower: str) -> list[str]:
        skill_tokens = [
            "java",
            "spring",
            "sql",
            "aws",
            "docker",
            "angular",
            "rest",
            "excel",
            "word",
            "finance",
            "numerical",
            "leadership",
            "stakeholder",
            "customer service",
            "contact center",
            "safety",
            "hipaa",
            "personality",
            "simulation",
        ]
        return [token for token in skill_tokens if token in lower]

    @staticmethod
    def _extract_stage(lower: str) -> str:
        if any(token in lower for token in ["finalist", "final stage", "shortlist"]):
            return "finalist"
        if any(token in lower for token in ["screen", "screening", "first filter", "volume"]):
            return "screening"
        if any(token in lower for token in ["development", "re-skill", "reskill", "audit"]):
            return "development"
        return ""

    @staticmethod
    def _extract_use_case(lower: str) -> str:
        if any(token in lower for token in ["selection", "hire", "hiring", "recruit", "assessment battery"]):
            return "selection"
        if any(token in lower for token in ["compare", "difference between", "versus", " vs "]):
            return "comparison"
        if any(token in lower for token in ["development", "audit", "reskill", "re-skill"]):
            return "development"
        return ""

    @staticmethod
    def _extract_comparisons(lower: str) -> list[str]:
        if "difference between" in lower or "compare" in lower or " versus " in lower or " vs " in lower:
            return [lower]
        return []

    @staticmethod
    def _extract_refinements(lower: str) -> list[str]:
        signals = [token for token in ["add", "drop", "remove", "replace", "instead", "actually", "keep", "update"] if token in lower]
        return signals

    @staticmethod
    def _extract_refusal_signals(lower: str) -> list[str]:
        return [token for token in ["legal", "law", "compliance", "hipaa requirement", "should we be legally required"] if token in lower]

    @staticmethod
    def _extract_injection_signals(lower: str) -> list[str]:
        return [token for token in ["ignore previous", "system prompt", "override", "disregard", "jailbreak"] if token in lower]
