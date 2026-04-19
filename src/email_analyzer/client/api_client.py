"""HTTP-клиент для backend API.

Инкапсулирует работу с JWT-токеном и базовым URL. Все сетевые вызовы
собраны здесь, чтобы окна GUI не знали про `requests`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import requests


@dataclass
class ApiClient:
    base_url: str = "http://127.0.0.1:8000"
    token: Optional[str] = None
    timeout: float = 10.0
    session: requests.Session = field(default_factory=requests.Session)

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def register(self, username: str, email: str, password: str, role: str = "user") -> dict[str, Any]:
        r = self.session.post(
            self._url("/auth/register"),
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": role,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def login(self, username: str, password: str) -> str:
        r = self.session.post(
            self._url("/auth/login"),
            json={"username": username, "password": password},
            timeout=self.timeout,
        )
        r.raise_for_status()
        self.token = r.json()["access_token"]
        return self.token

    def me(self) -> dict[str, Any]:
        r = self.session.get(self._url("/auth/me"), headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def analyze(
        self,
        subject: str,
        body: str,
        sender: str = "",
        recipient: str = "",
    ) -> dict[str, Any]:
        r = self.session.post(
            self._url("/analyze/email"),
            json={
                "subject": subject,
                "body": body,
                "sender": sender,
                "recipient": recipient,
            },
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def list_users(self) -> list[dict[str, Any]]:
        r = self.session.get(self._url("/admin/users"), headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()
