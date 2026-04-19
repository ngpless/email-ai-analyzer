"""Сервис управления пользователями (регистрация, логин, админка)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from email_analyzer.db.models import Role, User
from email_analyzer.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------- lookup ----------

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        return self.session.scalar(stmt)

    def list_all(self) -> list[User]:
        return list(self.session.scalars(select(User)))

    # ---------- mutation ----------

    def create(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = "",
        role: Role = Role.USER,
    ) -> User:
        if self.get_by_username(username) is not None:
            raise ValueError(f"user {username!r} already exists")
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name or None,
            role=role,
        )
        self.session.add(user)
        self.session.flush()
        return user

    def set_role(self, user_id: int, role: Role) -> User:
        user = self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"user {user_id} not found")
        user.role = role
        self.session.flush()
        return user

    def deactivate(self, user_id: int) -> User:
        user = self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"user {user_id} not found")
        user.is_active = False
        self.session.flush()
        return user

    # ---------- auth ----------

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(username)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(
            subject=str(user.id),
            extra={"username": user.username, "role": user.role.value},
        )
