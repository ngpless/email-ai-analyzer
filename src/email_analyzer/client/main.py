"""Точка входа PyQt6-клиента.

Запуск: `python -m email_analyzer.client.main`
"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from email_analyzer.client.state import AppState
from email_analyzer.client.windows import LoginWindow, MainWindow


class ClientApp:
    """Корневое управление приложением: логин → главное окно."""

    def __init__(self, argv: list[str]) -> None:
        self.qt_app = QApplication(argv)
        self.state = AppState()
        self.login: LoginWindow | None = None
        self.main: MainWindow | None = None

    def run(self) -> int:
        self.login = LoginWindow(self.state)
        self.login.logged_in.connect(self._on_login)
        self.login.show()
        return getattr(self.qt_app, "exec")()

    def _on_login(self, _user: dict) -> None:
        assert self.login is not None
        self.main = MainWindow(self.state)
        self.main.show()
        self.login.close()


def main() -> int:
    return ClientApp(sys.argv).run()


if __name__ == "__main__":
    raise SystemExit(main())
