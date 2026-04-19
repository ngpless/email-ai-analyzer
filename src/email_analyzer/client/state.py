"""Разделяемое состояние клиента (очень простое, без Redux-подобных паттернов)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from email_analyzer.client.api_client import ApiClient


@dataclass
class AppState:
    api: ApiClient = field(default_factory=ApiClient)
    current_user: Optional[dict[str, Any]] = None

    @property
    def is_admin(self) -> bool:
        return bool(self.current_user and self.current_user.get("role") == "admin")

    @property
    def username(self) -> str:
        if not self.current_user:
            return "(не авторизован)"
        return str(self.current_user.get("username", ""))
