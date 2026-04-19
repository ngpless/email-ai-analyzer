"""Простой анализатор тональности на лексиконе."""

from __future__ import annotations

from dataclasses import dataclass


POSITIVE_WORDS = frozenset({
    "спасибо", "благодар", "отлич", "супер", "рад", "класс",
    "прекрасно", "успех", "поздравля", "приятно", "хорош",
    "thanks", "thank you", "great", "excellent", "awesome", "happy",
})

NEGATIVE_WORDS = frozenset({
    "плохо", "ужас", "проблем", "ошибк", "провал", "разочарован",
    "жалоб", "недоволь", "срыв", "срочно исправ",
    "bad", "terrible", "awful", "failed", "problem", "complaint",
})


@dataclass(frozen=True, slots=True)
class SentimentResult:
    label: str  # positive / neutral / negative
    score: float  # [-1, 1]
    positive_hits: int
    negative_hits: int


class SentimentAnalyzer:
    def analyze(self, text: str) -> SentimentResult:
        t = text.lower()
        pos = sum(1 for w in POSITIVE_WORDS if w in t)
        neg = sum(1 for w in NEGATIVE_WORDS if w in t)
        total = pos + neg

        if total == 0:
            return SentimentResult(
                label="neutral", score=0.0,
                positive_hits=0, negative_hits=0,
            )

        score = (pos - neg) / total
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        return SentimentResult(
            label=label, score=score,
            positive_hits=pos, negative_hits=neg,
        )
