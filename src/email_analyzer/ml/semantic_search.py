"""Семантический поиск по почтовому архиву на базе TF-IDF + cosine.

Подход — offline, без embedding-моделей. Строит TF-IDF-матрицу по всем
индексированным письмам, запрос преобразует в тот же вектор, сортирует
по косинусной близости. Для каталога на 10k писем работает мгновенно.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True, slots=True)
class SearchHit:
    doc_index: int
    score: float


class SemanticSearch:
    def __init__(self) -> None:
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._documents: list[str] = []

    def index(self, documents: Sequence[str]) -> None:
        if not documents:
            self._documents = []
            self._vectorizer = None
            self._matrix = None
            return
        self._documents = list(documents)
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self._matrix = self._vectorizer.fit_transform(self._documents)

    def query(self, text: str, top_k: int = 5) -> list[SearchHit]:
        if self._vectorizer is None or self._matrix is None:
            return []
        q = self._vectorizer.transform([text])
        sims = cosine_similarity(q, self._matrix).ravel()
        # топ-k по убыванию
        order = np.argsort(sims)[::-1][:top_k]
        return [
            SearchHit(doc_index=int(i), score=float(sims[i]))
            for i in order
            if sims[i] > 0
        ]

    @property
    def size(self) -> int:
        return len(self._documents)
