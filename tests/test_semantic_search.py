"""Тесты SemanticSearch."""

from __future__ import annotations

from email_analyzer.ml.semantic_search import SemanticSearch


CORPUS = [
    "Совещание по проекту в 10:00",
    "Купить хлеб и сыр в магазине",
    "Отчёт о квартальной выручке прикреплён",
    "Напоминание о встрече с клиентом завтра",
    "Скидка 70% на зимнюю коллекцию",
]


def test_empty_index_returns_nothing():
    s = SemanticSearch()
    assert s.query("hello") == []


def test_exact_match_ranked_high():
    s = SemanticSearch()
    s.index(CORPUS)
    hits = s.query("совещание проект", top_k=2)
    assert hits
    assert CORPUS[hits[0].doc_index] == "Совещание по проекту в 10:00"


def test_unrelated_query_has_low_score_or_no_hits():
    s = SemanticSearch()
    s.index(CORPUS)
    hits = s.query("автомобиль самолёт ракета", top_k=5)
    # либо нет совпадений, либо скоры минимальные
    assert all(h.score < 0.2 for h in hits)


def test_top_k_respected():
    s = SemanticSearch()
    s.index(CORPUS)
    hits = s.query("отчёт клиент", top_k=2)
    assert len(hits) <= 2


def test_size_reported():
    s = SemanticSearch()
    s.index(CORPUS)
    assert s.size == len(CORPUS)
