"""Определение языка письма.

Работает по простой эвристике: считает процент кириллических букв vs
латинских. Достаточно для деловой переписки на RU/EN — без тяжёлых
моделей вроде fasttext-langid.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanguageResult:
    code: str  # ru / en / mixed / unknown
    ru_ratio: float
    en_ratio: float


class LanguageDetector:
    def __init__(self, mixed_threshold: float = 0.25) -> None:
        if not 0 < mixed_threshold < 0.5:
            raise ValueError("mixed_threshold must be in (0, 0.5)")
        self.mixed_threshold = mixed_threshold

    def detect(self, text: str) -> LanguageResult:
        ru = sum(1 for c in text if "а" <= c.lower() <= "я" or c in "ёЁ")
        en = sum(1 for c in text if "a" <= c.lower() <= "z")
        total = ru + en
        if total == 0:
            return LanguageResult(code="unknown", ru_ratio=0.0, en_ratio=0.0)

        ru_ratio = ru / total
        en_ratio = en / total

        if ru_ratio > 1 - self.mixed_threshold:
            code = "ru"
        elif en_ratio > 1 - self.mixed_threshold:
            code = "en"
        else:
            code = "mixed"
        return LanguageResult(code=code, ru_ratio=ru_ratio, en_ratio=en_ratio)
