"""Интеграционный тест /stats/compute."""

from __future__ import annotations


def test_stats_requires_auth(client):
    response = client.post("/stats/compute", json=[])
    assert response.status_code == 401


def test_stats_returns_breakdown(client):
    client.post(
        "/auth/register",
        json={
            "username": "statuser",
            "email": "statuser@ex.com",
            "password": "pw12345",
        },
    )
    token = client.post(
        "/auth/login",
        json={"username": "statuser", "password": "pw12345"},
    ).json()["access_token"]

    response = client.post(
        "/stats/compute",
        json=[
            {"category": "work", "confidence": 0.9, "is_spam": False},
            {"category": "spam", "confidence": 0.8, "is_spam": True},
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["spam_count"] == 1
    assert data["by_category"] == {"work": 1, "spam": 1}
