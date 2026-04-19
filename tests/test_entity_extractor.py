"""Тесты извлечения сущностей."""

from __future__ import annotations

from email_analyzer.ml import EntityExtractor


def test_extract_emails_and_urls():
    text = "Напиши на support@example.com или посмотри https://example.com/help"
    ents = EntityExtractor().extract(text)
    assert "support@example.com" in ents.emails
    assert "https://example.com/help" in ents.urls


def test_extract_dates_and_times():
    text = "Встреча 15.05.2026 в 10:30 или 2026-05-16"
    ents = EntityExtractor().extract(text)
    assert "15.05.2026" in ents.dates
    assert "2026-05-16" in ents.dates
    assert "10:30" in ents.times


def test_extract_date_word_form():
    ents = EntityExtractor().extract("Увидимся 10 мая на конференции.")
    assert any("мая" in d.lower() for d in ents.dates)


def test_extract_amount():
    ents = EntityExtractor().extract("Оплатите 1 500 рублей до пятницы.")
    assert any("руб" in a.lower() for a in ents.amounts)


def test_extract_tasks():
    ents = EntityExtractor().extract(
        "Прошу подготовить отчёт к среде. Также необходимо проверить смету."
    )
    assert len(ents.tasks) >= 1


def test_empty_text_returns_empty_bundle():
    ents = EntityExtractor().extract("")
    assert ents.emails == ()
    assert ents.urls == ()
