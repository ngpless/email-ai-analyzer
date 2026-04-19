"""Тесты суммаризатора."""

from __future__ import annotations

import pytest

from email_analyzer.ml import Summarizer


def test_empty_input_returns_empty():
    assert Summarizer().summarize("") == ""
    assert Summarizer().summarize("   ") == ""


def test_short_text_returned_as_is():
    text = "Это короткое письмо в одно предложение."
    out = Summarizer(max_sentences=3).summarize(text)
    assert text.strip().rstrip(".") in out


def test_long_text_compressed():
    long_text = " ".join(
        [
            "В понедельник состоится совещание.",
            "Нужно подготовить слайды и рассчитать бюджет.",
            "Также прошу проверить контракт с подрядчиком.",
            "Мама просила забрать посылку на почте.",
            "По дороге можно купить хлеб и сыр.",
        ]
    )
    s = Summarizer(max_sentences=2).summarize(long_text)
    assert s
    # В саммари должно остаться не больше двух предложений (~точек)
    assert s.count(".") <= 3  # допуск на внутренние точки


def test_max_sentences_must_be_positive():
    with pytest.raises(ValueError):
        Summarizer(max_sentences=0)
