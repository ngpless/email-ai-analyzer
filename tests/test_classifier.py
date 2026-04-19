"""Тесты классификатора писем."""

from __future__ import annotations

import pytest

from email_analyzer.db.models import Category
from email_analyzer.ml import EmailClassifier


@pytest.fixture
def trained_classifier() -> EmailClassifier:
    clf = EmailClassifier()
    clf.fit_seed()
    return clf


def test_predict_without_fitting_raises():
    clf = EmailClassifier()
    with pytest.raises(RuntimeError):
        clf.predict("какой-то текст")


def test_fit_requires_at_least_two_categories():
    clf = EmailClassifier()
    with pytest.raises(ValueError):
        clf.fit(
            ["a", "b", "c"],
            [Category.WORK, Category.WORK, Category.WORK],
        )


def test_seed_fit_makes_classifier_usable(trained_classifier: EmailClassifier):
    assert trained_classifier.is_fitted()
    result = trained_classifier.predict("Совещание в 10:00 по проекту")
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.top_scores) >= 2


def test_classifier_detects_work_email(trained_classifier: EmailClassifier):
    result = trained_classifier.predict(
        "Прошу согласовать смету по проекту до конца недели."
    )
    assert result.category in {Category.WORK, Category.IMPORTANT}


def test_classifier_detects_promo(trained_classifier: EmailClassifier):
    result = trained_classifier.predict(
        "Мегаскидка 70% на зимнюю коллекцию, только 3 дня!"
    )
    assert result.category in {Category.PROMO, Category.SPAM}


def test_classifier_save_and_load(trained_classifier: EmailClassifier, tmp_path):
    path = tmp_path / "clf.joblib"
    trained_classifier.save(path)
    assert path.exists()

    fresh = EmailClassifier()
    fresh.load(path)
    assert fresh.is_fitted()

    r1 = trained_classifier.predict("Скидка 50% сегодня")
    r2 = fresh.predict("Скидка 50% сегодня")
    assert r1.category == r2.category
    assert abs(r1.confidence - r2.confidence) < 1e-9
