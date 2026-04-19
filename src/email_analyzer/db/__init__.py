"""Слой базы данных: модели SQLAlchemy и сессия."""

from email_analyzer.db.models import (
    Attachment,
    Base,
    User,
    Role,
    EmailMessage,
    Classification,
    Rule,
    AnalysisReport,
)
from email_analyzer.db.session import get_engine, get_session, init_db

__all__ = [
    "Attachment",
    "Base",
    "User",
    "Role",
    "EmailMessage",
    "Classification",
    "Rule",
    "AnalysisReport",
    "get_engine",
    "get_session",
    "init_db",
]
