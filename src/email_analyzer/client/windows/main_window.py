"""Главное окно приложения со списком писем и меню."""

from __future__ import annotations

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDialog,
    QHeaderView,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from email_analyzer.client.state import AppState
from email_analyzer.client.windows.about_window import AboutWindow
from email_analyzer.client.windows.admin_window import AdminWindow
from email_analyzer.client.windows.email_detail_window import EmailDetailWindow
from email_analyzer.client.windows.help_window import HelpWindow
from email_analyzer.client.windows.import_dialog import ImportDialog
from email_analyzer.client.windows.profile_window import ProfileWindow
from email_analyzer.client.windows.reports_window import ReportsWindow
from email_analyzer.client.windows.rules_window import RulesWindow
from email_analyzer.client.windows.settings_window import SettingsWindow


def _run_modal(dialog: QDialog) -> bool:
    """Показать диалог модально и вернуть True, если принят."""
    return getattr(dialog, "exec")() == QDialog.DialogCode.Accepted


class MainWindow(QMainWindow):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWindowTitle(f"Email AI Analyzer — {state.username}")
        self.resize(1024, 640)

        self._subwindows: list[QWidget] = []
        self._emails: list[dict] = []

        self._build_menu()
        self._build_toolbar()
        self._build_central()
        self._build_status()

    def _build_menu(self) -> None:
        menubar: QMenuBar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(self._action("Импорт писем…", self._open_import))
        file_menu.addAction(self._action("Отчёты", self._open_reports))
        file_menu.addSeparator()
        file_menu.addAction(self._action("Выход", self.close))

        tools_menu = menubar.addMenu("Инструменты")
        tools_menu.addAction(self._action("Настройки", self._open_settings))
        tools_menu.addAction(self._action("Правила", self._open_rules))

        user_menu = menubar.addMenu("Пользователь")
        user_menu.addAction(self._action("Личный кабинет", self._open_profile))
        if self.state.is_admin:
            user_menu.addAction(self._action("Администрирование", self._open_admin))

        help_menu = menubar.addMenu("Справка")
        help_menu.addAction(self._action("Помощь", self._open_help))
        help_menu.addAction(self._action("О программе", self._open_about))

    def _build_toolbar(self) -> None:
        bar = QToolBar("Основное")
        bar.addAction(self._action("Импорт", self._open_import))
        bar.addAction(self._action("Настройки", self._open_settings))
        bar.addAction(self._action("Отчёты", self._open_reports))
        self.addToolBar(bar)

    def _build_central(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["От", "Тема", "Дата", "Категория", "Спам?"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._open_detail)
        layout.addWidget(self.table)

        self.setCentralWidget(central)

    def _build_status(self) -> None:
        bar = QStatusBar()
        bar.showMessage(f"Подключено: {self.state.api.base_url}")
        self.setStatusBar(bar)

    def _action(self, text: str, callback) -> QAction:
        a = QAction(text, self)
        a.triggered.connect(callback)
        return a

    def add_email(self, email: dict) -> None:
        self._emails.append(email)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(email.get("sender", "")))
        self.table.setItem(row, 1, QTableWidgetItem(email.get("subject", "")))
        self.table.setItem(row, 2, QTableWidgetItem(str(email.get("sent_at", ""))))
        self.table.setItem(row, 3, QTableWidgetItem(email.get("category", "")))
        self.table.setItem(row, 4, QTableWidgetItem("да" if email.get("is_spam") else "нет"))

    def _open_child(self, window: QWidget) -> None:
        self._subwindows.append(window)
        window.show()

    def _open_import(self) -> None:
        dlg = ImportDialog(self.state, self)
        if _run_modal(dlg):
            for email in dlg.collected:
                self.add_email(email)

    def _open_settings(self) -> None:
        self._open_child(SettingsWindow(self.state))

    def _open_reports(self) -> None:
        self._open_child(ReportsWindow(self.state, self._emails))

    def _open_rules(self) -> None:
        self._open_child(RulesWindow(self.state))

    def _open_profile(self) -> None:
        self._open_child(ProfileWindow(self.state))

    def _open_admin(self) -> None:
        if not self.state.is_admin:
            QMessageBox.warning(self, "Нет прав", "Нужна роль admin")
            return
        self._open_child(AdminWindow(self.state))

    def _open_help(self) -> None:
        self._open_child(HelpWindow())

    def _open_about(self) -> None:
        self._open_child(AboutWindow())

    def _open_detail(self, row: int, _column: int) -> None:
        if 0 <= row < len(self._emails):
            self._open_child(EmailDetailWindow(self._emails[row]))
