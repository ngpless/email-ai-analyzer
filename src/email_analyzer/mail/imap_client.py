"""IMAP-клиент (тонкая обёртка над `imaplib`).

Единственное назначение — изолировать сетевой ввод-вывод от остального
кода. В тестах подменяется через `FakeImapBackend`, который не делает
реальных сетевых вызовов.
"""

from __future__ import annotations

import imaplib
from dataclasses import dataclass
from typing import List, Optional, Protocol

from email_analyzer.mail.parser import ParsedEmail, parse_email_bytes


@dataclass(frozen=True, slots=True)
class ImapAccount:
    host: str
    port: int = 993
    username: str = ""
    password: str = ""
    use_ssl: bool = True


@dataclass(frozen=True, slots=True)
class FetchedEmail:
    uid: str
    parsed: ParsedEmail


class ImapBackend(Protocol):
    """Абстракция над реальным `imaplib.IMAP4`."""

    def login(self, username: str, password: str) -> None: ...
    def select(self, folder: str) -> List[str]: ...
    def search(self, criteria: str) -> List[str]: ...
    def fetch(self, uid: str) -> bytes: ...
    def logout(self) -> None: ...


class _RealImapBackend:
    """Реальная реализация через `imaplib`."""

    def __init__(self, account: ImapAccount, timeout: Optional[int] = None) -> None:
        cls = imaplib.IMAP4_SSL if account.use_ssl else imaplib.IMAP4
        self._conn = cls(account.host, account.port, timeout=timeout)

    def login(self, username: str, password: str) -> None:
        self._conn.login(username, password)

    def select(self, folder: str) -> List[str]:
        status, data = self._conn.select(folder, readonly=True)
        if status != "OK":
            raise RuntimeError(f"IMAP SELECT failed: {status}")
        return [b.decode() if isinstance(b, bytes) else b for b in data]

    def search(self, criteria: str) -> List[str]:
        status, data = self._conn.search(None, criteria)
        if status != "OK":
            raise RuntimeError(f"IMAP SEARCH failed: {status}")
        if not data or not data[0]:
            return []
        return data[0].decode().split()

    def fetch(self, uid: str) -> bytes:
        status, data = self._conn.fetch(uid, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            raise RuntimeError(f"IMAP FETCH failed for uid={uid}")
        first = data[0]
        if isinstance(first, tuple) and len(first) >= 2:
            return first[1]
        raise RuntimeError(f"unexpected IMAP FETCH payload for uid={uid}")

    def logout(self) -> None:
        try:
            self._conn.logout()
        except (OSError, imaplib.IMAP4.error):
            pass


class ImapClient:
    """Высокоуровневый клиент."""

    def __init__(
        self,
        account: ImapAccount,
        backend: Optional[ImapBackend] = None,
        timeout: int = 30,
    ) -> None:
        self.account = account
        self._backend: ImapBackend = backend or _RealImapBackend(account, timeout=timeout)
        self._logged_in = False

    def __enter__(self) -> "ImapClient":
        self.login()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def login(self) -> None:
        self._backend.login(self.account.username, self.account.password)
        self._logged_in = True

    def close(self) -> None:
        if self._logged_in:
            self._backend.logout()
            self._logged_in = False

    def fetch_recent(self, folder: str = "INBOX", limit: int = 20) -> List[FetchedEmail]:
        """Получить последние `limit` писем из папки."""
        if not self._logged_in:
            raise RuntimeError("not logged in")
        self._backend.select(folder)
        uids = self._backend.search("ALL")
        uids = uids[-limit:] if limit > 0 else uids

        result: List[FetchedEmail] = []
        for uid in uids:
            raw = self._backend.fetch(uid)
            parsed = parse_email_bytes(raw)
            result.append(FetchedEmail(uid=uid, parsed=parsed))
        return result
