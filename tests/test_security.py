"""Тесты аутентификационных утилит."""

from __future__ import annotations

from email_analyzer.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password_roundtrip():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_token_roundtrip():
    token = create_access_token(subject="42", extra={"role": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_invalid_token_returns_none():
    assert decode_access_token("definitely-not-a-token") is None
