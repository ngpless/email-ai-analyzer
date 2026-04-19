"""Импорт писем из .mbox (формат Thunderbird / Unix mailbox).

Используется для batch-загрузки писем из архивного файла без IMAP.
"""

from __future__ import annotations

import mailbox
from pathlib import Path
from typing import Iterator

from email_analyzer.mail.parser import ParsedEmail, parse_email_bytes


def import_mbox(path: Path) -> Iterator[ParsedEmail]:
    """Итерировать письма из .mbox-файла."""
    mbox = mailbox.mbox(str(path))
    try:
        for message in mbox:
            raw = message.as_bytes()
            yield parse_email_bytes(raw)
    finally:
        mbox.close()
