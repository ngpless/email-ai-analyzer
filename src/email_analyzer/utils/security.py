"""Хеширование паролей и JWT-токены."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from email_analyzer.config import get_settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain, hashed)
    except ValueError:
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
