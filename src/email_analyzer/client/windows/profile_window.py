"""Личный кабинет пользователя."""

from __future__ import annotations

from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from email_analyzer.client.state import AppState


class ProfileWindow(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Личный кабинет")
        self.resize(480, 320)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Личный кабинет</h2>"))

        form = QFormLayout()
        user = state.current_user or {}
        form.addRow("ID:", QLineEdit(str(user.get("id", ""))))
        form.addRow("Логин:", QLineEdit(user.get("username", "")))
        form.addRow("Email:", QLineEdit(user.get("email", "")))
        form.addRow("ФИО:", QLineEdit(user.get("full_name") or ""))
        form.addRow("Роль:", QLineEdit(user.get("role", "")))
        form.addRow("Активен:", QLineEdit("да" if user.get("is_active") else "нет"))

        wrapper = QWidget()
        wrapper.setLayout(form)
        layout.addWidget(wrapper)
