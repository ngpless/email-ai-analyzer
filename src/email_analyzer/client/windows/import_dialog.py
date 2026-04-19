"""Диалог импорта писем через IMAP + анализ каждого через API."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QSpinBox,
    QVBoxLayout,
)

from email_analyzer.client.state import AppState
from email_analyzer.mail import ImapAccount, ImapClient


class ImportDialog(QDialog):
    def __init__(self, state: AppState, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.collected: list[dict] = []

        self.setWindowTitle("Импорт писем из почтового ящика")
        self.resize(460, 300)

        outer = QVBoxLayout(self)

        form = QFormLayout()
        self.host = QLineEdit("imap.gmail.com")
        form.addRow("IMAP-сервер:", self.host)
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(993)
        form.addRow("Порт:", self.port)
        self.login = QLineEdit()
        form.addRow("Логин:", self.login)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Пароль:", self.password)
        self.limit = QSpinBox()
        self.limit.setRange(1, 500)
        self.limit.setValue(10)
        form.addRow("Сколько писем:", self.limit)
        self.use_ssl = QCheckBox("SSL")
        self.use_ssl.setChecked(True)
        form.addRow(self.use_ssl)
        outer.addLayout(form)

        self.progress = QProgressBar()
        outer.addWidget(self.progress)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._do_import)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def _do_import(self) -> None:
        account = ImapAccount(
            host=self.host.text().strip(),
            port=self.port.value(),
            username=self.login.text().strip(),
            password=self.password.text(),
            use_ssl=self.use_ssl.isChecked(),
        )
        try:
            with ImapClient(account) as client:
                fetched = client.fetch_recent(limit=self.limit.value())
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка IMAP", str(exc))
            return

        total = len(fetched)
        self.progress.setMaximum(max(total, 1))
        for i, item in enumerate(fetched, 1):
            parsed = item.parsed
            try:
                analysis = self.state.api.analyze(
                    subject=parsed.subject,
                    body=parsed.body,
                    sender=parsed.sender,
                    recipient=parsed.recipient,
                )
            except Exception as exc:
                QMessageBox.critical(self, "Ошибка анализа", str(exc))
                return
            self.collected.append({
                "sender": parsed.sender,
                "recipient": parsed.recipient,
                "subject": parsed.subject,
                "body": parsed.body,
                "sent_at": parsed.sent_at,
                "category": analysis["category"],
                "confidence": analysis["confidence"],
                "is_spam": analysis["is_spam"],
                "is_phishing": analysis["is_phishing"],
                "summary": analysis["summary"],
                "entities": analysis["entities"],
            })
            self.progress.setValue(i)

        self.accept()
