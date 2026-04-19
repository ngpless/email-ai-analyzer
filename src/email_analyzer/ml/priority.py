"""Оценка приоритета письма.

Комбинирует сигналы: важные слова в теме, срочные даты, роль отправителя,
категория классификатора. Возвращает score 0..1 и один из 4 уровней:
critical / high / normal / low.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from email_analyzer.db.models import Category


URGENT_MARKERS = (
    "срочно", "asap", "урген", "немедлен",
    "до конца дня", "до завтра", "critical",
)

IMPORTANT_SENDERS = ("boss", "ceo", "manager", "руководит", "директор")


@dataclass(frozen=True, slots=True)
class PriorityResult:
    level: str  # critical / high / normal / low
    score: float


class PriorityScorer:
    def score(
        self,
        subject: str,
        body: str,
        sender: str,
        category: Category | None = None,
    ) -> PriorityResult:
        text = f"{subject}\n{body}".lower()
        s = 0.0

        # Срочные маркеры в теме/теле
        urgent_hits = sum(1 for m in URGENT_MARKERS if m in text)
        s += min(urgent_hits * 0.25, 0.6)

        # Отправитель — «начальник»
        sender_l = sender.lower()
        if any(kw in sender_l for kw in IMPORTANT_SENDERS):
            s += 0.3

        # Восклицательные в теме
        if subject.count("!") >= 2:
            s += 0.1

        # Дедлайн сегодня/завтра в тексте
        if re.search(r"\bсегодня\b|\bзавтра\b|\btoday\b|\btomorrow\b", text):
            s += 0.15

        # Вклад категории
        if category is Category.IMPORTANT:
            s += 0.25
        elif category is Category.PHISHING:
            s += 0.4  # фишинг — критично
        elif category is Category.SPAM:
            s -= 0.3

        s = max(0.0, min(s, 1.0))

        if s >= 0.75:
            level = "critical"
        elif s >= 0.45:
            level = "high"
        elif s >= 0.15:
            level = "normal"
        else:
            level = "low"

        return PriorityResult(level=level, score=s)
