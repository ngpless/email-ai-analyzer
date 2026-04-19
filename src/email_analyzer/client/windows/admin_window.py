"""Панель администратора."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.client.state import AppState


class AdminWindow(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Администрирование")
        self.resize(720, 480)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Пользователи системы</h2>"))

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Логин", "Email", "Роль", "Активен"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        refresh = QPushButton("Обновить список")
        refresh.clicked.connect(self._refresh)
        layout.addWidget(refresh)

        self._refresh()

    def _refresh(self) -> None:
        try:
            users = self.state.api.list_users()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        self.table.setRowCount(0)
        for user in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(user["username"]))
            self.table.setItem(row, 2, QTableWidgetItem(user["email"]))
            self.table.setItem(row, 3, QTableWidgetItem(user["role"]))
            self.table.setItem(row, 4, QTableWidgetItem("да" if user["is_active"] else "нет"))
