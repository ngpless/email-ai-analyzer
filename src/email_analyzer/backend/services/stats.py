"""Статистика по почте пользователя."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from email_analyzer.db.models import Category


@dataclass(frozen=True, slots=True)
class MailStats:
    total: int
    by_category: dict[str, int]
    spam_count: int
    phishing_count: int
    avg_confidence: float


class StatsService:
    def compute(self, emails: Iterable[dict]) -> MailStats:
        emails_list = list(emails)
        total = len(emails_list)
        if total == 0:
            return MailStats(
                total=0, by_category={},
                spam_count=0, phishing_count=0, avg_confidence=0.0,
            )

        by_cat: dict[str, int] = {}
        spam = 0
        phishing = 0
        conf_sum = 0.0
        for email in emails_list:
            cat = str(email.get("category", Category.OTHER.value))
            by_cat[cat] = by_cat.get(cat, 0) + 1
            if email.get("is_spam"):
                spam += 1
            if email.get("is_phishing"):
                phishing += 1
            conf_sum += float(email.get("confidence", 0.0))

        return MailStats(
            total=total,
            by_category=by_cat,
            spam_count=spam,
            phishing_count=phishing,
            avg_confidence=conf_sum / total,
        )
