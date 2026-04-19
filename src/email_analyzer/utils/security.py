"""Хеширование паролей (bcrypt) и JWT-токены.

Используется библиотека `bcrypt` напрямую, без passlib: это избавляет
от известных несовместимостей между passlib и bcrypt ≥ 4.x.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from email_analyzer.config import get_settings


_ALGORITHM = "HS256"
_MAX_PASSWORD_BYTES = 72  # bcrypt ограничение


def _encode_password(plain: str) -> bytes:
    """Закодировать пароль в UTF-8 и обрезать до 72 байт (предел bcrypt)."""
    return plain.encode("utf-8")[:_MAX_PASSWORD_BYTES]


def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_encode_password(plain), bcrypt.gensalt())
    return hashed.decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_password(plain), hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    extra: Optional[dict[str, Any]] = None,
    ttl_minutes: Optional[int] = None,
) -> str:
    settings = get_settings()
    payload: dict[str, Any] = {"sub": subject}
    if extra:
        payload.update(extra)
    minutes = ttl_minutes if ttl_minutes is not None else settings.access_token_ttl_minutes
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    except JWTError:
        return None
