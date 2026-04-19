"""Экстрактивный суммаризатор.

Автор: Нефедов А. Г. (студ. билет 70200291).
Тема ВКР: «Разработка AI-приложения для анализа почтовых сообщений».

Выбираются наиболее «информативные» предложения текста по сумме
TF-IDF-весов слов в предложении. Подход относится к классической
центроидной экстрактивной суммаризации, ссылка: Radev et al., 2004
(«Centroid-based summarization of multiple documents»). Плюсы —
отсутствие внешних зависимостей, предсказуемость, пригодность для
офлайна. Минус — не выдаёт новые формулировки, но это для писем не
критично: их суть передаётся лучше в исходных предложениях.

Интерфейс написан так, чтобы при необходимости подменить его LLM-ом
(см. `ml/llm_provider.py`) без правки потребителей.
"""

from __future__ import annotations

import re
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Summarizer:
    def __init__(self, max_sentences: int = 3) -> None:
        if max_sentences < 1:
            raise ValueError("max_sentences must be ≥ 1")
        self.max_sentences = max_sentences

    def summarize(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""

        sentences = _split_sentences(text)
        if len(sentences) <= self.max_sentences:
            return " ".join(sentences).strip()

        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 1), min_df=1)
            matrix = vectorizer.fit_transform(sentences)
        except ValueError:
            return sentences[0]

        scores = np.asarray(matrix.sum(axis=1)).ravel()
        top_indices = np.argsort(scores)[-self.max_sentences:]
        top_indices.sort()  # сохраняем порядок
        selected = [sentences[i] for i in top_indices]
        return " ".join(selected).strip()


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[А-ЯA-ZЁ])")


def _split_sentences(text: str) -> List[str]:
    # Нормализуем пробелы
    text = re.sub(r"\s+", " ", text).strip()
    # Грубый разбор; достаточен для деловой переписки
    raw = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in raw if s.strip()]
