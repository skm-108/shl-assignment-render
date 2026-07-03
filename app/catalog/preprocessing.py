from __future__ import annotations

from dataclasses import dataclass, field

from app.models.catalog import CatalogItem, normalize_whitespace


def normalize_family_key(name: str) -> str:
    text = normalize_whitespace(name).lower()
    replacements = [
        "(new)",
        "new",
        "report",
        "solution",
        "bundle",
    ]
    for token in replacements:
        text = text.replace(token, " ")
    return " ".join(text.split())


@dataclass(slots=True)
class PreparedCatalog:
    items: list[CatalogItem]
    items_by_id: dict[str, CatalogItem] = field(default_factory=dict)
    items_by_alias: dict[str, set[str]] = field(default_factory=dict)
    items_by_family: dict[str, list[str]] = field(default_factory=dict)
    items_by_product_class: dict[str, list[str]] = field(default_factory=dict)
    items_by_test_type: dict[str, list[str]] = field(default_factory=dict)
    items_by_language: dict[str, list[str]] = field(default_factory=dict)
    items_by_job_level: dict[str, list[str]] = field(default_factory=dict)
    search_documents: dict[str, str] = field(default_factory=dict)


class CatalogPreprocessor:
    def prepare(self, items: list[CatalogItem]) -> PreparedCatalog:
        prepared = PreparedCatalog(items=items)

        for item in items:
            prepared.items_by_id[item.entity_id] = item
            prepared.search_documents[item.entity_id] = item.search_text

            family_key = normalize_family_key(item.name)
            prepared.items_by_family.setdefault(family_key, []).append(item.entity_id)
            prepared.items_by_product_class.setdefault(item.product_class, []).append(item.entity_id)
            prepared.items_by_test_type.setdefault(item.test_type or "unknown", []).append(item.entity_id)

            for language in item.languages:
                prepared.items_by_language.setdefault(language.lower(), []).append(item.entity_id)
            for level in item.job_levels:
                prepared.items_by_job_level.setdefault(level.lower(), []).append(item.entity_id)
            for alias in item.aliases:
                prepared.items_by_alias.setdefault(alias, set()).add(item.entity_id)

        return prepared
