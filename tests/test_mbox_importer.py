"""Тесты импорта из .mbox."""

from __future__ import annotations

from pathlib import Path

from email_analyzer.mail.mbox_importer import import_mbox


MBOX_CONTENT = """From - Mon Apr 19 10:00:00 2026
From: alice@example.com
To: bob@example.com
Subject: First message
Message-ID: <1@example.com>

Body of the first message.

From - Mon Apr 19 11:00:00 2026
From: charlie@example.com
To: bob@example.com
Subject: Second message
Message-ID: <2@example.com>

Body of the second message.
"""


def test_import_mbox_two_messages(tmp_path: Path):
    mbox_path = tmp_path / "archive.mbox"
    mbox_path.write_text(MBOX_CONTENT, encoding="utf-8")

    messages = list(import_mbox(mbox_path))
    assert len(messages) == 2
    assert messages[0].subject == "First message"
    assert messages[1].sender == "charlie@example.com"
