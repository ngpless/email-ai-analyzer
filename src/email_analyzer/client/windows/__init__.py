"""Все окна приложения (ровно 12 — требование методички ≥ 10)."""

from email_analyzer.client.windows.login_window import LoginWindow
from email_analyzer.client.windows.main_window import MainWindow
from email_analyzer.client.windows.email_detail_window import EmailDetailWindow
from email_analyzer.client.windows.settings_window import SettingsWindow
from email_analyzer.client.windows.admin_window import AdminWindow
from email_analyzer.client.windows.profile_window import ProfileWindow
from email_analyzer.client.windows.rules_window import RulesWindow
from email_analyzer.client.windows.reports_window import ReportsWindow
from email_analyzer.client.windows.help_window import HelpWindow
from email_analyzer.client.windows.about_window import AboutWindow
from email_analyzer.client.windows.stats_window import StatsWindow
from email_analyzer.client.windows.add_rule_dialog import AddRuleDialog
from email_analyzer.client.windows.import_dialog import ImportDialog

__all__ = [
    "LoginWindow",
    "MainWindow",
    "EmailDetailWindow",
    "SettingsWindow",
    "AdminWindow",
    "ProfileWindow",
    "RulesWindow",
    "ReportsWindow",
    "HelpWindow",
    "AboutWindow",
    "StatsWindow",
    "AddRuleDialog",
    "ImportDialog",
]
