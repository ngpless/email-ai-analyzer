"""Детектор спама и фишинга на эвристиках.

Автор: Нефедов А. Г. (студ. билет 70200291).
Тема ВКР: «Разработка AI-приложения для анализа почтовых сообщений».

Реализация намеренно простая и прозрачная: каждая сработавшая эвристика
добавляет вклад к score. Порог 0,5 = спам. Отдельный флаг фишинга
поднимается, если письмо притворяется банком или почтовым провайдером
и просит ввести данные.

Эвристический подход выбран в паре с ML-классификатором сознательно:
он ловит поведенческие паттерны (доля капса, количество «!», подмена
имени отправителя), которые TF-IDF на коротких темах видит плохо.
В итоге два модуля дополняют друг друга — что и отражено в сервисе
анализа.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


SPAM_KEYWORDS = (
    "выигр", "приз", "миллион", "халяв",
    "кредит без проверки", "viagra", "casino", "реклам",
    "только сегодня", "успей купить", "скид",
    "промокод", "супер акц",
)

PHISHING_KEYWORDS = (
    "введите пароль", "подтвердите пароль",
    "заблокирован", "ваш банк", "ваш аккаунт будет удал",
    "верификац", "введите cvv", "подтвердите данные карт",
    "iphone подарок", "срочно переход",
)

SUSPICIOUS_DOMAINS = (
    "bit.ly", "tinyurl.com", "goo.gl", "t.co",
    "xn--", "free-", "-secure-",
)


@dataclass(frozen=True, slots=True)
class SpamResult:
    is_spam: bool
    is_phishing: bool
    score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)


class SpamDetector:
    """Эвристический детектор."""

    def __init__(self, threshold: float = 0.5) -> None:
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold must be in (0, 1)")
        self.threshold = threshold

    def detect(self, subject: str, body: str, sender: str = "") -> SpamResult:
        text = f"{subject}\n{body}".lower()
        reasons: List[str] = []
        score = 0.0
        is_phishing = False

        # Ключевые слова спама
        spam_hits = sum(1 for kw in SPAM_KEYWORDS if kw in text)
        if spam_hits:
            contrib = min(0.15 * spam_hits, 0.6)
            score += contrib
            reasons.append(f"spam keywords: {spam_hits}")

        # Ключевые слова фишинга
        phishing_hits = sum(1 for kw in PHISHING_KEYWORDS if kw in text)
        if phishing_hits:
            is_phishing = True
            score += min(0.25 * phishing_hits, 0.7)
            reasons.append(f"phishing keywords: {phishing_hits}")

        # ПОДОЗРИТЕЛЬНЫЙ СУБДЖЕКТ КАПСОМ
        upper_ratio = _upper_ratio(subject)
        if upper_ratio > 0.6 and len(subject) > 6:
            score += 0.15
            reasons.append(f"shouting subject ({upper_ratio:.0%} caps)")

        # Много восклицательных знаков
        exc = subject.count("!") + body.count("!")
        if exc >= 3:
            score += 0.1
            reasons.append(f"excessive ! ({exc})")

        # Подозрительные домены-редиректоры
        for dom in SUSPICIOUS_DOMAINS:
            if dom in text:
                score += 0.2
                reasons.append(f"suspicious domain: {dom}")
                break

        # Поддельный отправитель «bank» / «paypal» но не с их домена
        if sender:
            sender_l = sender.lower()
            if re.search(r"(bank|paypal|google|apple|microsoft)", sender_l):
                if not re.search(
                    r"@(bank|paypal|google|apple|microsoft)\.",
                    sender_l,
                ):
                    is_phishing = True
                    score += 0.3
                    reasons.append("spoofed sender")

        score = min(score, 1.0)
        is_spam = score >= self.threshold

        return SpamResult(
            is_spam=is_spam,
            is_phishing=is_phishing,
            score=score,
            reasons=tuple(reasons),
        )


def _upper_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    upper = sum(1 for c in letters if c.isupper())
    return upper / len(letters)
