"""Функциональное тестирование (method of black box).

Метод тестирования №3 по методичке ГИА-2025. Проверяем систему как
единое целое, не заглядывая во внутренности: отправляем HTTP-запросы,
сверяем ответ с ожидаемым поведением.

Отличие от модульных: здесь нас не интересует, как устроен классификатор
или какой ключ используется в JWT — только что «спам помечен как спам»,
«не-админу доступ 403», «регистрация возвращает 201».
"""

from __future__ import annotations

import pytest


@pytest.fixture
def authed_token(client) -> str:
    client.post(
        "/auth/register",
        json={"username": "func", "email": "func@ex.com", "password": "secret1"},
    )
    r = client.post(
        "/auth/login",
        json={"username": "func", "password": "secret1"},
    )
    return r.json()["access_token"]


def _analyze(client, token: str, **kwargs) -> dict:
    r = client.post(
        "/analyze/email",
        json=kwargs,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    return r.json()


class TestSpamRecognition:
    """Функциональные сценарии для детекции спама/фишинга."""

    def test_obvious_spam_is_flagged(self, client, authed_token):
        data = _analyze(
            client, authed_token,
            subject="ВЫ ВЫИГРАЛИ МИЛЛИОН!!!",
            body="Срочно перейдите по ссылке, промокод BONUS.",
            sender="promo@shop.ru",
        )
        assert data["is_spam"] is True
        assert data["spam_score"] >= 0.5

    def test_phishing_spoofed_sender(self, client, authed_token):
        data = _analyze(
            client, authed_token,
            subject="Подтвердите пароль",
            body="Ваш аккаунт будет удалён, введите CVV.",
            sender="security@paypal-fake.ru",
        )
        assert data["is_phishing"] is True

    def test_legitimate_work_email_is_not_spam(self, client, authed_token):
        data = _analyze(
            client, authed_token,
            subject="Совещание перенесено",
            body="Коллеги, встреча во вторник в 15:00.",
            sender="pm@company.com",
        )
        assert data["is_spam"] is False
        assert data["is_phishing"] is False


class TestEntityExtraction:
    def test_date_and_time_extracted(self, client, authed_token):
        data = _analyze(
            client, authed_token,
            subject="Встреча",
            body="Созвон 20.05.2026 в 14:30, подключайтесь.",
            sender="a@b.c",
        )
        assert any("20.05.2026" in d for d in data["entities"]["dates"])
        assert "14:30" in data["entities"]["times"]

    def test_money_extracted(self, client, authed_token):
        data = _analyze(
            client, authed_token,
            subject="Счёт",
            body="К оплате 15 000 рублей до пятницы.",
            sender="x@y.z",
        )
        assert any("руб" in a.lower() for a in data["entities"]["amounts"])


class TestAccessControl:
    def test_non_admin_cannot_access_admin_endpoints(self, client):
        client.post(
            "/auth/register",
            json={"username": "plain", "email": "plain@ex.com", "password": "pw12345"},
        )
        token = client.post(
            "/auth/login",
            json={"username": "plain", "password": "pw12345"},
        ).json()["access_token"]

        r = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 403

    def test_unauthenticated_requests_rejected(self, client):
        r = client.post("/analyze/email", json={"subject": "x", "body": "y"})
        assert r.status_code == 401

    def test_admin_can_list_users(self, client):
        client.post(
            "/auth/register",
            json={
                "username": "boss",
                "email": "boss@ex.com",
                "password": "pw12345",
                "role": "admin",
            },
        )
        token = client.post(
            "/auth/login",
            json={"username": "boss", "password": "pw12345"},
        ).json()["access_token"]

        r = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
