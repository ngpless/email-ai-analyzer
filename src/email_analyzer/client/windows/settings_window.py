"""Окно настроек — ≥ 5 пунктов меню (IMAP, ML, категории, уведомления, экспорт)."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.client.state import AppState


class SettingsWindow(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle("Настройки")
        self.resize(560, 440)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        tabs.addTab(self._imap_tab(), "Почта (IMAP)")
        tabs.addTab(self._ml_tab(), "ML-модель")
        tabs.addTab(self._categories_tab(), "Категории")
        tabs.addTab(self._notifications_tab(), "Уведомления")
        tabs.addTab(self._export_tab(), "Экспорт")

        layout.addWidget(tabs)

        buttons = QWidget()
        buttons_layout = QVBoxLayout(buttons)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.close)
        buttons_layout.addWidget(save_btn)
        layout.addWidget(buttons)

    def _imap_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.addRow("Сервер:", QLineEdit("imap.gmail.com"))
        form.addRow("Порт:", QSpinBox())
        form.addRow("Логин:", QLineEdit())
        form.addRow("Пароль:", QLineEdit())
        ssl = QCheckBox("Использовать SSL")
        ssl.setChecked(True)
        form.addRow(ssl)
        return w

    def _ml_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        engine = QComboBox()
        engine.addItems(["Локальная (TF-IDF + LogReg)", "OpenAI GPT", "Yandex GPT", "GigaChat"])
        form.addRow("Движок:", engine)
        form.addRow("Порог спама:", QLineEdit("0.5"))
        form.addRow("Макс. длина саммари:", QSpinBox())
        return w

    def _categories_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Категории классификации:"))
        items = QListWidget()
        items.addItems([
            "Работа", "Личное", "Реклама", "Спам",
            "Фишинг", "Важное", "Другое",
        ])
        layout.addWidget(items)
        return w

    def _notifications_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QCheckBox("Уведомлять о письмах категории «важное»"))
        form.addRow(QCheckBox("Уведомлять о фишинге"))
        form.addRow(QCheckBox("Звуковой сигнал"))
        form.addRow("Интервал опроса, минут:", QSpinBox())
        return w

    def _export_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.addRow(QCheckBox("Автосохранение отчётов в .xlsx"))
        form.addRow(QCheckBox("Автосохранение отчётов в .docx"))
        form.addRow("Папка экспорта:", QLineEdit("./reports"))
        return w
