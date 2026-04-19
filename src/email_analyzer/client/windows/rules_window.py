"""Окно управления правилами автообработки писем."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.client.state import AppState
from email_analyzer.client.windows.add_rule_dialog import AddRuleDialog


def _open_modal(dialog: QDialog) -> bool:
    return getattr(dialog, "exec")() == QDialog.DialogCode.Accepted


class RulesWindow(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Правила")
        self.resize(640, 440)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Имя", "Поле", "Шаблон", "Действие"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        add = QPushButton("Добавить правило")
        add.clicked.connect(self._add_rule)
        remove = QPushButton("Удалить выбранное")
        remove.clicked.connect(self._remove_rule)
        buttons.addWidget(add)
        buttons.addWidget(remove)
        layout.addLayout(buttons)

    def _add_rule(self) -> None:
        dlg = AddRuleDialog(self)
        if _open_modal(dlg):
            rule = dlg.rule
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(rule["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(rule["field"]))
            self.table.setItem(row, 2, QTableWidgetItem(rule["pattern"]))
            self.table.setItem(row, 3, QTableWidgetItem(rule["action"]))

    def _remove_rule(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
