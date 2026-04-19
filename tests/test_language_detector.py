"""Тесты LanguageDetector."""

from __future__ import annotations

import pytest

from email_analyzer.ml.language_detector import LanguageDetector


@pytest.fixture
def detector() -> LanguageDetector:
    return LanguageDetector()


def test_detect_russian(detector):
    result = detector.detect("Привет, это тестовое сообщение")
    assert result.code == "ru"
    assert result.ru_ratio > 0.9


def test_detect_english(detector):
    result = detector.detect("Hello, this is a test message")
    assert result.code == "en"
    assert result.en_ratio > 0.9


def test_detect_mixed(detector):
    result = detector.detect("Hello Привет hybrid message тест")
    assert result.code == "mixed"


def test_detect_unknown_for_empty(detector):
    result = detector.detect("")
    assert result.code == "unknown"


def test_detect_unknown_for_numbers_only(detector):
    result = detector.detect("12345 67890 !!!")
    assert result.code == "unknown"


def test_invalid_threshold():
    with pytest.raises(ValueError):
        LanguageDetector(mixed_threshold=0.0)
    with pytest.raises(ValueError):
        LanguageDetector(mixed_threshold=0.5)
