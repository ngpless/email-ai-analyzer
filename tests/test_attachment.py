"""Тесты модели Attachment."""

from __future__ import annotations

from email_analyzer.db.models import Attachment, EmailMessage, User


def test_create_attachment(db_session):
    user = User(username="u", email="u@ex.com", password_hash="h")
    db_session.add(user)
    db_session.flush()
    email = EmailMessage(
        owner_id=user.id,
        message_id="<m@x>",
        sender="a@b.c",
        recipient="u@ex.com",
        subject="s",
        body="b",
    )
    db_session.add(email)
    db_session.flush()

    att = Attachment(
        email_id=email.id,
        filename="report.pdf",
        mime_type="application/pdf",
        size_bytes=12_345,
    )
    db_session.add(att)
    db_session.commit()

    assert att.id is not None
    assert att.filename == "report.pdf"
    assert att.size_bytes == 12_345
