"""Окно авторизации."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.client.state import AppState


class LoginWindow(QWidget):
    logged_in = pyqtSignal(dict)

    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Email AI Analyzer — Вход")
        self.resize(360, 200)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Логин:"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Пароль:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self._on_register)
        layout.addWidget(self.register_btn)

    def _on_login(self) -> None:
        username = self.username.text().strip()
        password = self.password.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните логин и пароль")
            return
        try:
            self.state.api.login(username, password)
            self.state.current_user = self.state.api.me()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка входа", str(exc))
            return
        self.logged_in.emit(self.state.current_user)

    def _on_register(self) -> None:
        username = self.username.text().strip()
        password = self.password.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните логин и пароль")
            return
        try:
            self.state.api.register(
                username=username,
                email=f"{username}@local.test",
                password=password,
            )
            QMessageBox.information(self, "OK", "Пользователь создан. Войдите.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка регистрации", str(exc))
