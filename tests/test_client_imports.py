"""Smoke-тесты: все окна и точка входа клиента успешно импортируются.

Не запускаем полноценный GUI (нет дисплея в CI), но проверяем, что
код синтаксически и импортно корректен, и что насчитывается ≥ 10 окон
(требование методички).
"""

from __future__ import annotations


def test_all_windows_importable():
    from email_analyzer.client import windows as w

    expected = {
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
        "AddRuleDialog",
        "ImportDialog",
    }

    assert expected.issubset(set(w.__all__))
    # Методичка требует ≥ 10 оконных форм
    assert len(w.__all__) >= 10


def test_client_main_importable():
    from email_analyzer.client import main as client_main

    assert hasattr(client_main, "main")
    assert hasattr(client_main, "ClientApp")


def test_api_client_importable():
    from email_analyzer.client.api_client import ApiClient

    client = ApiClient(base_url="http://example.test")
    assert client.base_url == "http://example.test"
    assert client.token is None
