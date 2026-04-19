"""Модели SQLAlchemy.

ER-схема:

    Role ────< User ────< EmailMessage ────< Classification
                 │
                 └────< Rule
                 └────< AnalysisReport

- Role         — роль пользователя (admin / analyst / user)
- User         — пользователь системы
- EmailMessage — письмо, загруженное из IMAP
- Classification — результат автоклассификации письма
- Rule         — пользовательское правило обработки
- AnalysisReport — сформированный отчёт (.docx/.xlsx)
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Role(str, Enum):
    """Роли пользователей."""

    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"


class Category(str, Enum):
    """Категории классификации писем."""

    WORK = "work"
    PERSONAL = "personal"
    PROMO = "promo"
    SPAM = "spam"
    PHISHING = "phishing"
    IMPORTANT = "important"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    full_name: Mapped[Optional[str]] = mapped_column(String(128))
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    emails: Mapped[List["EmailMessage"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    rules: Mapped[List["Rule"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    reports: Mapped[List["AnalysisReport"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User #{self.id} {self.username} ({self.role.value})>"


class EmailMessage(Base):
    __tablename__ = "emails"
    __table_args__ = (UniqueConstraint("owner_id", "message_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    message_id: Mapped[str] = mapped_column(String(255), index=True)
    sender: Mapped[str] = mapped_column(String(255))
    recipient: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    is_read: Mapped[bool] = mapped_column(default=False)

    owner: Mapped[User] = relationship(back_populates="emails")
    classification: Mapped[Optional["Classification"]] = relationship(
        back_populates="email",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Email #{self.id} from={self.sender!r} subject={self.subject!r}>"


class Attachment(Base):
    """Вложение письма (имя, mime, размер)."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_id: Mapped[int] = mapped_column(ForeignKey("emails.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_id: Mapped[int] = mapped_column(
        ForeignKey("emails.id"), unique=True, index=True
    )
    category: Mapped[Category] = mapped_column(SQLEnum(Category))
    confidence: Mapped[float] = mapped_column(default=0.0)
    is_spam: Mapped[bool] = mapped_column(default=False)
    is_phishing: Mapped[bool] = mapped_column(default=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    entities_json: Mapped[Optional[str]] = mapped_column(Text)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    email: Mapped[EmailMessage] = relationship(back_populates="classification")


class Rule(Base):
    """Пользовательское правило автоклассификации или уведомления."""

    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    pattern: Mapped[str] = mapped_column(String(512))
    field: Mapped[str] = mapped_column(String(32), default="subject")  # subject/body/sender
    action_category: Mapped[Optional[Category]] = mapped_column(SQLEnum(Category))
    notify: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    owner: Mapped[User] = relationship(back_populates="rules")


class AnalysisReport(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    path: Mapped[str] = mapped_column(String(512))
    format: Mapped[str] = mapped_column(String(16))  # docx / xlsx
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    owner: Mapped[User] = relationship(back_populates="reports")
