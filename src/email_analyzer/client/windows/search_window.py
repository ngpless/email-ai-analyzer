"""Окно семантического поиска по почте."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.ml.semantic_search import SemanticSearch


class SearchWindow(QWidget):
    def __init__(self, emails: list[dict]) -> None:
        super().__init__()
        self._emails = emails
        self.setWindowTitle("Поиск по смыслу")
        self.resize(720, 480)

        self._search = SemanticSearch()
        corpus = [
            f"{e.get('subject', '')} {e.get('body', '')}"
            for e in emails
        ]
        if corpus:
            self._search.index(corpus)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Индексировано писем: {self._search.size}"))

        row = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Введите запрос…")
        find_btn = QPushButton("Искать")
        find_btn.clicked.connect(self._on_search)
        row.addWidget(self.query_input)
        row.addWidget(find_btn)
        layout.addLayout(row)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Score", "От", "Тема"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def _on_search(self) -> None:
        query = self.query_input.text().strip()
        self.table.setRowCount(0)
        if not query or self._search.size == 0:
            return
        hits = self._search.query(query, top_k=10)
        for hit in hits:
            email = self._emails[hit.doc_index]
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"{hit.score:.3f}"))
            self.table.setItem(row, 1, QTableWidgetItem(email.get("sender", "")))
            self.table.setItem(row, 2, QTableWidgetItem(email.get("subject", "")))
