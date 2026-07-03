from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.catalog import (
    CatalogItem,
    build_aliases,
    build_search_text,
    derive_product_class,
    derive_test_type,
    normalize_list,
    normalize_whitespace,
)


class CatalogLoadError(RuntimeError):
    """Raised when the catalog cannot be parsed after normalization."""


class CatalogLoader:
    def __init__(self, source_path: str | Path) -> None:
        self.source_path = Path(source_path)

    def load(self) -> list[CatalogItem]:
        raw_text = self.source_path.read_text(encoding="utf-8", errors="replace")
        cleaned_text = self._clean_catalog_text(raw_text)
        try:
            raw_records = json.loads(cleaned_text)
        except json.JSONDecodeError as exc:  # pragma: no cover - exercised through file-based validation
            raise CatalogLoadError(f"Unable to parse catalog at {self.source_path}") from exc
        if not isinstance(raw_records, list):
            raise CatalogLoadError("Catalog root must be a JSON array")
        return [self._normalize_record(record) for record in raw_records if isinstance(record, dict)]

    @staticmethod
    def _clean_catalog_text(raw_text: str) -> str:
        start_index = raw_text.find("[")
        if start_index >= 0:
            raw_text = raw_text[start_index:]

        cleaned: list[str] = []
        in_string = False
        escape = False

        for character in raw_text:
            if in_string:
                if escape:
                    cleaned.append(character)
                    escape = False
                elif character == "\\":
                    cleaned.append(character)
                    escape = True
                elif character == '"':
                    cleaned.append(character)
                    in_string = False
                elif character in "\n\r\t" or ord(character) < 32:
                    cleaned.append(" ")
                else:
                    cleaned.append(character)
            else:
                cleaned.append(character)
                if character == '"':
                    in_string = True
                    escape = False

        return "".join(cleaned)

    @staticmethod
    def _normalize_record(record: dict[str, Any]) -> CatalogItem:
        name = normalize_whitespace(str(record.get("name", "")))
        description = normalize_whitespace(str(record.get("description", "")))
        keys = normalize_list(record.get("keys", []))
        aliases = build_aliases(name, description, keys)
        test_type = derive_test_type(keys)
        product_class = derive_product_class(name, description)
        item = CatalogItem(
            entity_id=normalize_whitespace(str(record.get("entity_id", ""))),
            name=name,
            url=normalize_whitespace(str(record.get("link", ""))),
            scraped_at=normalize_whitespace(str(record.get("scraped_at", ""))),
            job_levels=normalize_list(record.get("job_levels", [])),
            languages=normalize_list(record.get("languages", [])),
            duration=normalize_whitespace(str(record.get("duration", ""))),
            status=normalize_whitespace(str(record.get("status", ""))),
            remote=normalize_whitespace(str(record.get("remote", ""))),
            adaptive=normalize_whitespace(str(record.get("adaptive", ""))),
            description=description,
            keys=keys,
            test_type=test_type,
            product_class=product_class,
            aliases=aliases,
            source=record,
        )
        item.search_text = build_search_text(item)
        return item


def load_catalog_items(source_path: str | Path) -> list[CatalogItem]:
    return CatalogLoader(source_path).load()
