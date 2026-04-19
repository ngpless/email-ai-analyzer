"""Парсер MIME-писем в простой dataclass.

Вынесен в отдельный модуль — чтобы можно было тестировать без реального
IMAP-сервера, просто скармливая сырые байты.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email import message_from_bytes, policy
from email.message import EmailMessage as StdEmailMessage
from email.utils import parsedate_to_datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
class ParsedEmail:
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    sent_at: Optional[datetime]


def parse_email_bytes(raw: bytes) -> ParsedEmail:
    """Распарсить сырое письмо в IANA-стандартный формат."""
    msg: StdEmailMessage = message_from_bytes(raw, policy=policy.default)  # type: ignore[assignment]

    subject = _header(msg, "Subject")
    sender = _header(msg, "From")
    recipient = _header(msg, "To")
    message_id = _header(msg, "Message-ID") or _fallback_id(sender, subject)

    sent_at: Optional[datetime] = None
    date_raw = _header(msg, "Date")
    if date_raw:
        try:
            sent_at = parsedate_to_datetime(date_raw)
        except (TypeError, ValueError):
            sent_at = None

    body = _extract_body(msg)

    return ParsedEmail(
        message_id=message_id,
        sender=sender,
        recipient=recipient,
        subject=subject,
        body=body,
        sent_at=sent_at,
    )


def _header(msg: StdEmailMessage, name: str) -> str:
    value = msg.get(name)
    if value is None:
        return ""
    return str(value).strip()


def _fallback_id(sender: str, subject: str) -> str:
    base = f"{sender}|{subject}"
    return f"<no-id-{hash(base) & 0xFFFFFFFF:x}@local>"


def _extract_body(msg: StdEmailMessage) -> str:
    """Достать плейн-текст (если нет — HTML без тегов, грубо)."""
    if msg.is_multipart():
        plain_parts: list[str] = []
        html_parts: list[str] = []
        for part in msg.walk():
            ctype = part.get_content_type()
            if part.get_content_disposition() == "attachment":
                continue
            if ctype == "text/plain":
                plain_parts.append(_decode_part(part))
            elif ctype == "text/html":
                html_parts.append(_decode_part(part))
        if plain_parts:
            return "\n".join(p for p in plain_parts if p)
        if html_parts:
            return _strip_html("\n".join(html_parts))
        return ""
    return _decode_part(msg)


def _decode_part(part: StdEmailMessage) -> str:
    try:
        content = part.get_content()
    except (LookupError, UnicodeDecodeError):
        payload = part.get_payload(decode=True) or b""
        return payload.decode("utf-8", errors="replace")
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return str(content)


def _strip_html(text: str) -> str:
    import re

    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
