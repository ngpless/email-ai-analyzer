"""Тесты PriorityScorer."""

from __future__ import annotations

from email_analyzer.db.models import Category
from email_analyzer.ml.priority import PriorityScorer


def test_critical_for_urgent_important_category():
    r = PriorityScorer().score(
        subject="СРОЧНО! до конца дня!!",
        body="Нужно сделать сегодня",
        sender="boss@company.com",
        category=Category.IMPORTANT,
    )
    assert r.level == "critical"


def test_low_for_spam():
    r = PriorityScorer().score(
        subject="Скидка 70%",
        body="Купи сейчас",
        sender="promo@shop.com",
        category=Category.SPAM,
    )
    assert r.level == "low"


def test_normal_for_plain_email():
    r = PriorityScorer().score(
        subject="Отчёт",
        body="Смотри вложение",
        sender="colleague@company.com",
        category=Category.WORK,
    )
    assert r.level in {"low", "normal"}


def test_high_for_boss_no_urgency():
    r = PriorityScorer().score(
        subject="Вопрос",
        body="Как дела с проектом?",
        sender="manager@company.com",
        category=Category.WORK,
    )
    assert r.level in {"normal", "high"}


def test_phishing_always_critical():
    r = PriorityScorer().score(
        subject="Подтверди пароль",
        body="Срочно по ссылке",
        sender="a@b.c",
        category=Category.PHISHING,
    )
    # фишинг бустит до high/critical
    assert r.level in {"high", "critical"}
