from __future__ import annotations

from dataclasses import dataclass, field
import re

from app.models.catalog import CatalogItem, normalize_whitespace


_DURATION_PATTERN = re.compile(r"(\d+)")


def parse_duration_minutes(duration: str) -> int | None:
    text = normalize_whitespace(duration).lower()
    if not text or text in {"-", "untimed", "variable"}:
        return None
    match = _DURATION_PATTERN.search(text)
    if not match:
        return None
    return int(match.group(1))


@dataclass(slots=True)
class FilterCriteria:
    job_levels: set[str] = field(default_factory=set)
    languages: set[str] = field(default_factory=set)
    product_classes: set[str] = field(default_factory=set)
    test_types: set[str] = field(default_factory=set)
    min_duration_minutes: int | None = None
    max_duration_minutes: int | None = None
    allow_untimed: bool = True
    require_remote: str | None = None
    require_adaptive: str | None = None


class MetadataFilter:
    def matches(self, item: CatalogItem, criteria: FilterCriteria | None = None) -> bool:
        if criteria is None:
            return True

        if criteria.job_levels and not self._matches_any(criteria.job_levels, item.job_levels):
            return False
        if criteria.languages and not self._matches_any(criteria.languages, item.languages):
            return False
        if criteria.product_classes and item.product_class not in criteria.product_classes:
            return False
        if criteria.test_types and item.test_type not in criteria.test_types:
            return False
        if criteria.require_remote and item.remote.lower() != criteria.require_remote.lower():
            return False
        if criteria.require_adaptive and item.adaptive.lower() != criteria.require_adaptive.lower():
            return False

        duration_minutes = parse_duration_minutes(item.duration)
        if duration_minutes is None and not criteria.allow_untimed:
            return False
        if duration_minutes is not None:
            if criteria.min_duration_minutes is not None and duration_minutes < criteria.min_duration_minutes:
                return False
            if criteria.max_duration_minutes is not None and duration_minutes > criteria.max_duration_minutes:
                return False
        return True

    @staticmethod
    def _matches_any(expected: set[str], actual: list[str]) -> bool:
        actual_normalized = {normalize_whitespace(value).lower() for value in actual}
        expected_normalized = {normalize_whitespace(value).lower() for value in expected}
        return bool(actual_normalized.intersection(expected_normalized))

    def filter(self, items: list[CatalogItem], criteria: FilterCriteria | None = None) -> list[CatalogItem]:
        return [item for item in items if self.matches(item, criteria)]
