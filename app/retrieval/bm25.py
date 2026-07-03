from __future__ import annotations

import math
import re
from dataclasses import dataclass
from collections import Counter, defaultdict
from typing import Iterable, Sequence


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


@dataclass(slots=True)
class BM25Document:
    item_id: str
    text: str


@dataclass(slots=True)
class BM25Hit:
    item_id: str
    score: float
    text: str


class BM25Index:
    def __init__(self, documents: Sequence[BM25Document], k1: float = 1.5, b: float = 0.75) -> None:
        self.documents = list(documents)
        self.k1 = k1
        self.b = b
        self.document_tokens = [tokenize(document.text) for document in self.documents]
        self.document_lengths = [len(tokens) for tokens in self.document_tokens]
        self.average_document_length = sum(self.document_lengths) / max(len(self.document_lengths), 1)
        self.document_frequencies = defaultdict(int)
        for tokens in self.document_tokens:
            for term in set(tokens):
                self.document_frequencies[term] += 1

    @classmethod
    def from_pairs(cls, pairs: Iterable[tuple[str, str]]) -> BM25Index:
        documents = [BM25Document(item_id=item_id, text=text) for item_id, text in pairs]
        return cls(documents)

    def score(self, query: str) -> list[BM25Hit]:
        query_terms = tokenize(query)
        if not query_terms:
            return [BM25Hit(item_id=document.item_id, score=0.0, text=document.text) for document in self.documents]

        hits: list[BM25Hit] = []
        document_count = max(len(self.documents), 1)
        for document, tokens, doc_length in zip(self.documents, self.document_tokens, self.document_lengths):
            token_counts = Counter(tokens)
            score = 0.0
            for term in query_terms:
                frequency = token_counts.get(term)
                if not frequency:
                    continue
                document_frequency = self.document_frequencies.get(term, 0)
                idf = math.log(1 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5))
                denominator = frequency + self.k1 * (1 - self.b + self.b * (doc_length / max(self.average_document_length, 1e-9)))
                score += idf * (frequency * (self.k1 + 1)) / denominator
            hits.append(BM25Hit(item_id=document.item_id, score=score, text=document.text))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)
