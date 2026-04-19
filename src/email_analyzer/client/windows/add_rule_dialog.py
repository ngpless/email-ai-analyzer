"""Диалог добавления правила — обязательное «диалоговое окно для
получения данных от пользователя со специальной формы» (методичка)."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)


class AddRuleDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Новое правило")
        self.resize(420, 220)

        form = QFormLayout(self)

        self.name = QLineEdit()
        form.addRow("Имя правила:", self.name)

        self.field = QComboBox()
        self.field.addItems(["subject", "body", "sender"])
        form.addRow("Поле:", self.field)

        self.pattern = QLineEdit()
        form.addRow("Шаблон (regex):", self.pattern)

        self.action = QComboBox()
        self.action.addItems([
            "Пометить как работа",
            "Пометить как важное",
            "Пометить как спам",
            "Уведомить",
        ])
        form.addRow("Действие:", self.action)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    @property
    def rule(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "field": self.field.currentText(),
            "pattern": self.pattern.text().strip(),
            "action": self.action.currentText(),
        }

    def _accept(self) -> None:
        if not self.name.text().strip() or not self.pattern.text().strip():
            QMessageBox.warning(self, "Проверка", "Заполните имя и шаблон")
            return
        self.accept()
