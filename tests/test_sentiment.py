"""Тесты SentimentAnalyzer."""

from __future__ import annotations

from email_analyzer.ml.sentiment import SentimentAnalyzer


def test_positive():
    r = SentimentAnalyzer().analyze("Спасибо, отличная работа! Класс!")
    assert r.label == "positive"
    assert r.score > 0


def test_negative():
    r = SentimentAnalyzer().analyze("Это ужасно, сплошные проблемы и ошибки.")
    assert r.label == "negative"
    assert r.score < 0


def test_neutral_no_sentiment_words():
    r = SentimentAnalyzer().analyze("Встреча в понедельник в 10:00.")
    assert r.label == "neutral"
    assert r.positive_hits == 0
    assert r.negative_hits == 0


def test_english_positive():
    r = SentimentAnalyzer().analyze("Great job, thanks!")
    assert r.label == "positive"
