"""Тесты IMAP-клиента через фейковый backend (без сетевого ввода-вывода)."""

from __future__ import annotations

from typing import List

from email_analyzer.mail import ImapAccount, ImapClient


class FakeBackend:
    def __init__(self, raw_emails: List[bytes]) -> None:
        self._emails = raw_emails
        self.calls: list[str] = []
        self.logged_in = False

    def login(self, username: str, password: str) -> None:
        self.calls.append(f"login:{username}")
        self.logged_in = True

    def select(self, folder: str) -> list[str]:
        self.calls.append(f"select:{folder}")
        return [str(len(self._emails))]

    def search(self, criteria: str) -> list[str]:
        self.calls.append(f"search:{criteria}")
        return [str(i + 1) for i in range(len(self._emails))]

    def fetch(self, uid: str) -> bytes:
        self.calls.append(f"fetch:{uid}")
        return self._emails[int(uid) - 1]

    def logout(self) -> None:
        self.calls.append("logout")
        self.logged_in = False


RAW = (
    b"From: sender@example.com\r\n"
    b"To: me@example.com\r\n"
    b"Subject: Test {n}\r\n"
    b"Message-ID: <id-{n}@example.com>\r\n"
    b"\r\n"
    b"Body {n}\r\n"
)


def test_fetch_recent_returns_all_emails():
    raw_emails = [RAW.replace(b"{n}", str(i).encode()) for i in range(3)]
    backend = FakeBackend(raw_emails)

    account = ImapAccount(host="imap.test", username="u", password="p")
    with ImapClient(account, backend=backend) as client:
        fetched = client.fetch_recent(limit=10)

    assert len(fetched) == 3
    assert fetched[0].parsed.subject == "Test 0"
    assert backend.calls[0] == "login:u"
    assert backend.calls[-1] == "logout"


def test_limit_respected():
    raw_emails = [RAW.replace(b"{n}", str(i).encode()) for i in range(5)]
    backend = FakeBackend(raw_emails)

    account = ImapAccount(host="imap.test", username="u", password="p")
    with ImapClient(account, backend=backend) as client:
        fetched = client.fetch_recent(limit=2)

    assert len(fetched) == 2
    assert fetched[-1].parsed.subject == "Test 4"
