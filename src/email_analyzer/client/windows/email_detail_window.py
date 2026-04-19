"""Окно просмотра письма с результатом анализа."""

from __future__ import annotations

import json

from PyQt6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class EmailDetailWindow(QWidget):
    def __init__(self, email: dict) -> None:
        super().__init__()
        self.setWindowTitle(f"Письмо: {email.get('subject', '')}")
        self.resize(680, 520)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>От:</b> {email.get('sender', '')}"))
        layout.addWidget(QLabel(f"<b>Кому:</b> {email.get('recipient', '')}"))
        layout.addWidget(QLabel(f"<b>Тема:</b> {email.get('subject', '')}"))
        layout.addWidget(QLabel(f"<b>Категория:</b> {email.get('category', '')}"))
        layout.addWidget(QLabel(
            f"<b>Уверенность:</b> {email.get('confidence', 0):.2f}; "
            f"<b>Спам:</b> {'да' if email.get('is_spam') else 'нет'}; "
            f"<b>Фишинг:</b> {'да' if email.get('is_phishing') else 'нет'}"
        ))

        layout.addWidget(QLabel("<b>Саммари:</b>"))
        summary = QPlainTextEdit(email.get("summary", ""))
        summary.setReadOnly(True)
        summary.setMaximumHeight(120)
        layout.addWidget(summary)

        layout.addWidget(QLabel("<b>Извлечённые сущности:</b>"))
        entities = QPlainTextEdit(
            json.dumps(email.get("entities", {}), ensure_ascii=False, indent=2)
        )
        entities.setReadOnly(True)
        entities.setMaximumHeight(160)
        layout.addWidget(entities)

        layout.addWidget(QLabel("<b>Тело письма:</b>"))
        body = QPlainTextEdit(email.get("body", ""))
        body.setReadOnly(True)
        layout.addWidget(body)
