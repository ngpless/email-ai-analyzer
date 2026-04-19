"""Тесты StatsService."""

from __future__ import annotations

from email_analyzer.backend.services.stats import StatsService


def test_empty_input():
    stats = StatsService().compute([])
    assert stats.total == 0
    assert stats.by_category == {}
    assert stats.avg_confidence == 0.0


def test_aggregates_correctly():
    data = [
        {"category": "work", "confidence": 0.9, "is_spam": False, "is_phishing": False},
        {"category": "work", "confidence": 0.8, "is_spam": False, "is_phishing": False},
        {"category": "spam", "confidence": 0.7, "is_spam": True, "is_phishing": False},
        {"category": "phishing", "confidence": 0.95, "is_spam": True, "is_phishing": True},
    ]
    stats = StatsService().compute(data)
    assert stats.total == 4
    assert stats.by_category == {"work": 2, "spam": 1, "phishing": 1}
    assert stats.spam_count == 2
    assert stats.phishing_count == 1
    assert 0.8 < stats.avg_confidence < 0.9
