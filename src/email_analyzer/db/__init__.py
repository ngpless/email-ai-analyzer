"""Слой базы данных: модели SQLAlchemy и сессия."""

from email_analyzer.db.models import (
    AnalysisReport,
    Attachment,
    AuditLogEntry,
    Base,
    Classification,
    EmailLabel,
    EmailMessage,
    EmailThread,
    ImapAccount,
    Label,
    ModelVersion,
    Notification,
    Role,
    Rule,
    TrainingSample,
    User,
)
from email_analyzer.db.session import get_engine, get_session, init_db

__all__ = [
    "AnalysisReport",
    "Attachment",
    "AuditLogEntry",
    "Base",
    "Classification",
    "EmailLabel",
    "EmailMessage",
    "EmailThread",
    "ImapAccount",
    "Label",
    "ModelVersion",
    "Notification",
    "Role",
    "Rule",
    "TrainingSample",
    "User",
    "get_engine",
    "get_session",
    "init_db",
]
