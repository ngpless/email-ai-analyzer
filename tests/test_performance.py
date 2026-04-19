"""Нагрузочное (производительное) тестирование.

Метод тестирования №2 по методичке ГИА-2025 (п. 3, раздел 3 —
«не менее 4-х методов тестирования»).

Цель: убедиться, что при пиковой нагрузке API и ML-ядро работают в
пределах SLA — 2 секунды на письмо, согласно нефункциональному
требованию в ТЗ (docs/tz.md).
"""

from __future__ import annotations

import time

import pytest

from email_analyzer.backend.services.analysis import AnalysisService


@pytest.fixture(scope="module")
def service() -> AnalysisService:
    return AnalysisService()


def test_single_email_latency_under_sla(service: AnalysisService):
    """Анализ одного письма должен укладываться в 2 секунды."""
    start = time.perf_counter()
    service.analyze(
        subject="Совещание в понедельник",
        body="Коллеги, прошу согласовать повестку к 10:00.",
        sender="manager@company.com",
    )
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"Задержка {elapsed:.3f} с превышает SLA 2 с"


def test_batch_throughput(service: AnalysisService):
    """Обработка пакета из 50 писем должна занимать менее 30 секунд.

    Это соответствует заявленному в ТЗ ожиданию — не более 4 минут на
    100 писем, то есть 0,4 секунды на письмо в среднем.
    """
    texts = [
        ("Совещание в 10:00", "Коллеги, повестка прикреплена."),
        ("Скидка 50% только сегодня", "Успей купить!"),
        ("Ваш банк заблокировал карту", "Срочно введите пароль по ссылке."),
        ("Поздравляю с ДР!", "Желаю всего лучшего."),
        ("Отчёт готов", "Ссылка на доках."),
    ] * 10

    start = time.perf_counter()
    for subject, body in texts:
        service.analyze(subject=subject, body=body, sender="x@y.z")
    elapsed = time.perf_counter() - start

    assert elapsed < 30.0, f"Пакет 50 писем обработан за {elapsed:.2f} с (> 30 с)"
    per_email = elapsed / 50
    assert per_email < 0.5, f"Среднее время {per_email:.3f} с/письмо превышает 0,5 с"


def test_classifier_is_not_leaking_memory():
    """После 1000 вызовов предсказателя размер внутренних структур
    не должен непропорционально расти.

    Тест-индикатор: проверяем, что классификатор переиспользует
    обученный pipeline, а не обучает его каждый раз заново.
    """
    service = AnalysisService()
    pipeline_before = service.classifier._pipeline  # type: ignore[attr-defined]

    for i in range(1000):
        service.analyze(
            subject=f"Test {i}",
            body="Короткое тестовое сообщение.",
            sender="test@test.com",
        )

    pipeline_after = service.classifier._pipeline  # type: ignore[attr-defined]
    assert pipeline_before is pipeline_after, "pipeline не должен пересоздаваться"
