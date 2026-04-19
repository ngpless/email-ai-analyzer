"""Тесты оркестрирующего сервиса анализа."""

from __future__ import annotations

from email_analyzer.backend.services.analysis import AnalysisService
from email_analyzer.db.models import Category


def test_analyze_work_email_returns_classification():
    service = AnalysisService()
    result = service.analyze(
        subject="Совещание в понедельник в 10:30",
        body=(
            "Коллеги, прошу согласовать повестку. "
            "Обсудим статус проекта и распределение задач."
        ),
        sender="boss@company.com",
    )
    assert result.category in {
        Category.WORK,
        Category.IMPORTANT,
    }
    assert result.is_spam is False


def test_analyze_obvious_spam_marks_spam():
    service = AnalysisService()
    result = service.analyze(
        subject="ВЫИГРАЙ МИЛЛИОН!!!",
        body="Только сегодня! Успей получить приз, промокод: SPAM. Супер акция!",
        sender="noreply@promo.shop",
    )
    assert result.is_spam is True
    assert result.category in {Category.SPAM, Category.PHISHING, Category.PROMO}


def test_analyze_phishing_detected():
    service = AnalysisService()
    result = service.analyze(
        subject="Ваш банк заблокирован",
        body="Подтвердите пароль по ссылке, иначе аккаунт будет удалён.",
        sender="security@paypal-fake.ru",
    )
    assert result.is_phishing is True
    assert result.category == Category.PHISHING


def test_analyze_extracts_entities():
    service = AnalysisService()
    result = service.analyze(
        subject="Счёт",
        body="Оплата 3 500 рублей до 01.05.2026, ref@company.com",
    )
    assert any("руб" in a.lower() for a in result.entities["amounts"])
    assert "01.05.2026" in result.entities["dates"]
    assert "ref@company.com" in result.entities["emails"]


def test_summary_non_empty_for_multi_sentence():
    service = AnalysisService()
    result = service.analyze(
        subject="Проект",
        body=(
            "Завтра встреча. Нужно обсудить статус. "
            "Также прошу подготовить смету. И сделать презентацию."
        ),
    )
    assert result.summary
