"""Окно статистики по импортированной почте."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.backend.services.stats import StatsService


class StatsWindow(QWidget):
    def __init__(self, emails: list[dict]) -> None:
        super().__init__()
        self.setWindowTitle("Статистика")
        self.resize(520, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Сводная статистика</h2>"))

        stats = StatsService().compute(emails)

        layout.addWidget(QLabel(f"<b>Всего писем:</b> {stats.total}"))
        layout.addWidget(QLabel(f"<b>Спам:</b> {stats.spam_count}"))
        layout.addWidget(QLabel(f"<b>Фишинг:</b> {stats.phishing_count}"))
        layout.addWidget(QLabel(f"<b>Средняя уверенность:</b> {stats.avg_confidence:.2f}"))

        layout.addWidget(QLabel("<b>По категориям:</b>"))
        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Категория", "Количество"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for cat, count in sorted(stats.by_category.items(), key=lambda p: -p[1]):
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(cat))
            table.setItem(row, 1, QTableWidgetItem(str(count)))
        layout.addWidget(table)
