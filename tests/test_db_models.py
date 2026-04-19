"""Тесты моделей БД."""

from __future__ import annotations

from email_analyzer.db.models import (
    Category,
    Classification,
    EmailMessage,
    Role,
    User,
)


def test_create_user_with_default_role(db_session):
    user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.role is Role.USER
    assert user.is_active is True


def test_create_email_with_classification(db_session):
    user = User(
        username="bob",
        email="bob@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    db_session.flush()

    email = EmailMessage(
        owner_id=user.id,
        message_id="<m1@test>",
        sender="sender@example.com",
        recipient="bob@example.com",
        subject="Hello",
        body="Test body",
    )
    db_session.add(email)
    db_session.flush()

    email.classification = Classification(
        email_id=email.id,
        category=Category.WORK,
        confidence=0.9,
        is_spam=False,
        is_phishing=False,
    )
    db_session.commit()

    loaded = db_session.get(EmailMessage, email.id)
    assert loaded is not None
    assert loaded.classification is not None
    assert loaded.classification.category is Category.WORK


def test_email_unique_per_owner(db_session):
    user = User(username="c", email="c@ex.com", password_hash="h")
    db_session.add(user)
    db_session.flush()

    email1 = EmailMessage(
        owner_id=user.id,
        message_id="<same@id>",
        sender="a@b.c",
        recipient="c@d.e",
        subject="s",
        body="b",
    )
    email2 = EmailMessage(
        owner_id=user.id,
        message_id="<same@id>",
        sender="a@b.c",
        recipient="c@d.e",
        subject="s2",
        body="b2",
    )
    db_session.add_all([email1, email2])

    import pytest
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        db_session.commit()
