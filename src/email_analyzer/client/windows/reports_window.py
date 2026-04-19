"""Окно экспорта отчётов в .docx/.xlsx (требование методички)."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.client.state import AppState
from email_analyzer.utils.reports import (
    export_emails_to_docx,
    export_emails_to_xlsx,
)


class ReportsWindow(QWidget):
    def __init__(self, state: AppState, emails: list[dict]) -> None:
        super().__init__()
        self.state = state
        self._emails = emails
        self.setWindowTitle("Отчёты")
        self.resize(480, 260)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Экспорт отчёта</h2>"))
        layout.addWidget(QLabel(f"Писем в выгрузке: {len(emails)}"))

        docx_btn = QPushButton("Сохранить как .docx")
        docx_btn.clicked.connect(self._save_docx)
        layout.addWidget(docx_btn)

        xlsx_btn = QPushButton("Сохранить как .xlsx")
        xlsx_btn.clicked.connect(self._save_xlsx)
        layout.addWidget(xlsx_btn)

    def _save_docx(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить .docx", "report.docx", "Word (*.docx)"
        )
        if not path:
            return
        try:
            export_emails_to_docx(self._emails, Path(path))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        QMessageBox.information(self, "Готово", f"Сохранено: {path}")

    def _save_xlsx(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить .xlsx", "report.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        try:
            export_emails_to_xlsx(self._emails, Path(path))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        QMessageBox.information(self, "Готово", f"Сохранено: {path}")
