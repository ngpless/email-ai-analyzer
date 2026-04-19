"""Тесты детектора спама и фишинга."""

from __future__ import annotations

import pytest

from email_analyzer.ml import SpamDetector


@pytest.fixture
def detector() -> SpamDetector:
    return SpamDetector()


def test_normal_email_is_not_spam(detector):
    result = detector.detect(
        subject="Встреча в понедельник",
        body="Привет! Предлагаю встретиться в 10:00 в офисе.",
    )
    assert result.is_spam is False
    assert result.is_phishing is False
    assert result.score < 0.5


def test_obvious_spam_is_flagged(detector):
    result = detector.detect(
        subject="ВЫ ВЫИГРАЛИ МИЛЛИОН!!! Только сегодня!",
        body="Срочно перейдите по ссылке, чтобы забрать приз. Промокод BONUS.",
    )
    assert result.is_spam is True
    assert result.score >= 0.5
    assert result.reasons


def test_phishing_detected(detector):
    result = detector.detect(
        subject="Ваш банк заблокирован",
        body="Срочно подтвердите пароль, иначе ваш аккаунт будет удалён.",
        sender="security@banking-alert.xn--sec-example.com",
    )
    assert result.is_phishing is True


def test_sender_spoof_detected(detector):
    result = detector.detect(
        subject="Notification",
        body="Please verify your account",
        sender="security@paypal-fake.ru",
    )
    # «paypal» в имени, но не с домена paypal.*
    assert result.is_phishing is True


def test_threshold_must_be_valid():
    with pytest.raises(ValueError):
        SpamDetector(threshold=0.0)
    with pytest.raises(ValueError):
        SpamDetector(threshold=1.0)
