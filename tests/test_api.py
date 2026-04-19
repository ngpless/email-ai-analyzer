"""Интеграционные тесты REST API через FastAPI TestClient."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _register(client: TestClient, username: str, password: str, role: str = "user"):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
            "full_name": username.title(),
            "role": role,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_health_endpoint(client):
    assert client.get("/").status_code == 404  # root не подключён в тестовом app
    # но /auth/register работает
    r = client.post(
        "/auth/register",
        json={
            "username": "health_user",
            "email": "h@example.com",
            "password": "secret1",
        },
    )
    assert r.status_code == 201


def test_register_and_login(client):
    _register(client, "alice", "secret1")
    token = _login(client, "alice", "secret1")
    assert token

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_login_with_wrong_password(client):
    _register(client, "bob", "secret1")
    r = client.post(
        "/auth/login",
        json={"username": "bob", "password": "WRONG"},
    )
    assert r.status_code == 401


def test_analyze_email_endpoint_requires_auth(client):
    r = client.post(
        "/analyze/email",
        json={"subject": "hi", "body": "hello"},
    )
    assert r.status_code == 401


def test_analyze_email_endpoint_with_auth(client):
    _register(client, "analyst", "pw12345", role="analyst")
    token = _login(client, "analyst", "pw12345")
    r = client.post(
        "/analyze/email",
        json={
            "subject": "Совещание в понедельник",
            "body": "Коллеги, прошу согласовать повестку.",
            "sender": "pm@company.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "category" in data
    assert "confidence" in data
    assert "summary" in data


def test_admin_endpoints_require_admin_role(client):
    _register(client, "regular", "pw12345", role="user")
    token = _login(client, "regular", "pw12345")
    r = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_can_list_users(client):
    _register(client, "root", "pw12345", role="admin")
    _register(client, "other", "pw12345")
    token = _login(client, "root", "pw12345")
    r = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert {u["username"] for u in data} >= {"root", "other"}
