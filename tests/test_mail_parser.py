"""Тесты парсера MIME."""

from __future__ import annotations

from email_analyzer.mail.parser import parse_email_bytes


SIMPLE_PLAIN = (
    b"From: sender@example.com\r\n"
    b"To: recipient@example.com\r\n"
    b"Subject: Hello world\r\n"
    b'Message-ID: <abc123@example.com>\r\n'
    b"Date: Mon, 19 Apr 2026 10:30:00 +0300\r\n"
    b"Content-Type: text/plain; charset=utf-8\r\n"
    b"\r\n"
    b"This is a simple plain-text email.\r\n"
)


def test_parse_plain_email():
    email = parse_email_bytes(SIMPLE_PLAIN)
    assert email.sender == "sender@example.com"
    assert email.recipient == "recipient@example.com"
    assert email.subject == "Hello world"
    assert email.message_id == "<abc123@example.com>"
    assert "simple plain-text" in email.body
    assert email.sent_at is not None


def test_missing_message_id_gets_fallback():
    raw = (
        b"From: a@b.c\r\n"
        b"To: c@d.e\r\n"
        b"Subject: No ID\r\n"
        b"\r\n"
        b"body\r\n"
    )
    email = parse_email_bytes(raw)
    assert email.message_id.startswith("<no-id-")


def test_html_part_gets_stripped():
    raw = (
        b"From: a@b.c\r\n"
        b"To: c@d.e\r\n"
        b"Subject: HTML only\r\n"
        b"MIME-Version: 1.0\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"\r\n"
        b"<html><body><p>Hello <b>world</b></p></body></html>\r\n"
    )
    email = parse_email_bytes(raw)
    assert "Hello" in email.body
    assert "<" not in email.body
