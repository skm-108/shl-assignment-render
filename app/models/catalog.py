from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


TEST_TYPE_CODES = {
    "Ability & Aptitude": "A",
    "Assessment Exercises": "E",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S",
}


@dataclass(slots=True)
class CatalogItem:
    entity_id: str
    name: str
    url: str
    scraped_at: str
    job_levels: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    duration: str = ""
    status: str = ""
    remote: str = ""
    adaptive: str = ""
    description: str = ""
    keys: list[str] = field(default_factory=list)
    test_type: str = ""
    product_class: str = "assessment"
    aliases: list[str] = field(default_factory=list)
    search_text: str = ""
    source: dict[str, Any] = field(default_factory=dict)


def derive_test_type(keys: list[str]) -> str:
    codes = [TEST_TYPE_CODES[key] for key in keys if key in TEST_TYPE_CODES]
    return ",".join(dict.fromkeys(codes))


def derive_product_class(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    if "report" in text:
        return "report"
    if any(token in text for token in ["solution", "bundle", "profiler cards", "job profiling guide"]):
        return "solution"
    if any(token in text for token in ["guide", "cards"]):
        return "guide"
    return "assessment"


def normalize_whitespace(value: str) -> str:
    return " ".join(value.replace("\u00a0", " ").split())


def normalize_list(values: list[Any] | Any) -> list[str]:
    if not isinstance(values, list):
        return []
    cleaned = []
    for value in values:
        if value is None:
            continue
        text = normalize_whitespace(str(value))
        if text:
            cleaned.append(text)
    return cleaned


def build_aliases(name: str, description: str, keys: list[str]) -> list[str]:
    aliases = {
        normalize_whitespace(name).lower(),
        normalize_whitespace(name).replace("(New)", "").strip().lower(),
        normalize_whitespace(name).replace("(new)", "").strip().lower(),
    }
    if description:
        aliases.add(normalize_whitespace(description).lower())
    for key in keys:
        aliases.add(key.lower())
    return sorted(alias for alias in aliases if alias)


def build_search_text(item: CatalogItem) -> str:
    parts = [
        item.name,
        item.description,
        " ".join(item.job_levels),
        " ".join(item.languages),
        " ".join(item.keys),
        item.product_class,
        item.test_type,
        " ".join(item.aliases),
    ]
    return normalize_whitespace(" ".join(part for part in parts if part))
