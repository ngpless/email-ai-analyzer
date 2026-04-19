"""Валидационное тестирование (boundary / edge cases).

Метод тестирования №4 по методичке. Проверяем реакцию системы на
крайние и некорректные входные данные: пустые строки, очень длинные
тексты, отсутствующие поля, экзотические символы.

Цель — убедиться, что API выдаёт осмысленные коды ответа (200 / 422 /
401), а ML-ядро не падает на нестандартных входах.
"""

from __future__ import annotations


def _register_and_login(client, username: str = "validator") -> str:
    client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@ex.com",
            "password": "pw12345",
        },
    )
    return client.post(
        "/auth/login",
        json={"username": username, "password": "pw12345"},
    ).json()["access_token"]


def test_empty_body_is_accepted(client):
    """Пустое тело письма — валидный вход (пустое письмо бывает)."""
    token = _register_and_login(client, "emptybody")
    r = client.post(
        "/analyze/email",
        json={"subject": "hello", "body": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "category" in data


def test_very_long_body_handled(client):
    """Тело длиной 100 000 символов не должно ронять API."""
    token = _register_and_login(client, "longbody")
    huge = "Коллеги, прошу согласовать. " * 3500  # ≈ 100KB
    r = client.post(
        "/analyze/email",
        json={"subject": "long", "body": huge},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200


def test_missing_password_returns_validation_error(client):
    r = client.post(
        "/auth/register",
        json={"username": "incomplete", "email": "ic@ex.com"},
    )
    assert r.status_code == 422


def test_invalid_email_format_rejected(client):
    r = client.post(
        "/auth/register",
        json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "pw12345",
        },
    )
    assert r.status_code == 422


def test_weak_password_rejected_by_minlength(client):
    r = client.post(
        "/auth/register",
        json={
            "username": "weakpw",
            "email": "weakpw@ex.com",
            "password": "abc",  # меньше 6 символов
        },
    )
    assert r.status_code == 422


def test_expired_or_invalid_token_rejected(client):
    r = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer definitely-not-a-valid-token"},
    )
    assert r.status_code == 401


def test_cyrillic_and_emoji_in_body(client):
    """Поддержка любых символов юникода."""
    token = _register_and_login(client, "unicode")
    r = client.post(
        "/analyze/email",
        json={
            "subject": "Привет 👋",
            "body": "Всё хорошо 😊🎉 до пятницы!",
            "sender": "друг@mail.ru",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200


def test_duplicate_username_rejected(client):
    client.post(
        "/auth/register",
        json={"username": "dup", "email": "a@ex.com", "password": "pw12345"},
    )
    r = client.post(
        "/auth/register",
        json={"username": "dup", "email": "b@ex.com", "password": "pw12345"},
    )
    assert r.status_code == 400


def test_wrong_password_returns_401(client):
    client.post(
        "/auth/register",
        json={"username": "x", "email": "x@ex.com", "password": "correct1"},
    )
    r = client.post(
        "/auth/login",
        json={"username": "x", "password": "wrong1"},
    )
    assert r.status_code == 401
