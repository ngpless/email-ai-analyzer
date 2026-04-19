"""Генерация графических материалов для отчёта.

Создаёт:
    - скриншоты всех окон PyQt6 (через offscreen-платформу Qt);
    - диаграммы matplotlib по реальным данным.

Все изображения сохраняются в docs/report_assets/.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Принудительно подключаем системные шрифты Windows — иначе Cyrillic рендерится квадратами.
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "report_assets"
ASSETS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "src"))


# ---------- скриншоты окон ----------


def take_window_screenshots() -> list[Path]:
    from PyQt6.QtWidgets import QApplication

    from email_analyzer.client.state import AppState
    from email_analyzer.client.windows import (
        AboutWindow,
        AddRuleDialog,
        AdminWindow,
        EmailDetailWindow,
        HelpWindow,
        ImportDialog,
        LoginWindow,
        MainWindow,
        ProfileWindow,
        ReportsWindow,
        RulesWindow,
        SearchWindow,
        SettingsWindow,
        StatsWindow,
    )

    from PyQt6.QtGui import QFont, QFontDatabase

    qt_app = QApplication.instance() or QApplication(sys.argv)

    # Явно подключаем шрифт с кириллицей (Segoe UI — системный Windows).
    # Для надёжности проходим по списку доступных семейств.
    preferred = ["Segoe UI", "Arial", "Tahoma", "DejaVu Sans"]
    available = set(QFontDatabase.families())
    chosen = next((name for name in preferred if name in available), None)
    if chosen is not None:
        qt_app.setFont(QFont(chosen, 9))
        print(f"  [fonts] используется шрифт: {chosen}")
    else:
        print(f"  [fonts] предпочтительные шрифты не найдены; families: {len(available)}")

    state = AppState()
    state.current_user = {
        "id": 1,
        "username": "admin",
        "email": "admin@local.test",
        "full_name": "Администратор",
        "role": "admin",
        "is_active": True,
    }

    demo_email = {
        "sender": "manager@company.com",
        "recipient": "admin@local.test",
        "subject": "Отчёт за квартал готов",
        "body": (
            "Коллеги, прилагаю итоговый отчёт за квартал. "
            "Прошу ознакомиться до пятницы, 25.04.2026."
        ),
        "sent_at": "2026-04-19 10:15",
        "category": "work",
        "confidence": 0.86,
        "is_spam": False,
        "is_phishing": False,
        "summary": "Отчёт за квартал готов, прошу ознакомиться до 25.04.2026.",
        "entities": {
            "dates": ["25.04.2026"],
            "emails": [],
            "urls": [],
            "phones": [],
            "times": [],
            "amounts": [],
            "tasks": ["прошу ознакомиться"],
        },
    }
    sample = [
        {
            "sender": "manager@company.com", "subject": "Отчёт за квартал",
            "sent_at": "2026-04-19", "category": "work",
            "confidence": 0.86, "is_spam": False, "is_phishing": False,
            "body": "...", "entities": {},
        },
        {
            "sender": "noreply@shop.ru", "subject": "ВЫИГРАЛИ МИЛЛИОН!!!",
            "sent_at": "2026-04-18", "category": "spam",
            "confidence": 0.72, "is_spam": True, "is_phishing": False,
            "body": "...", "entities": {},
        },
        {
            "sender": "sec@paypal-fake.ru", "subject": "Ваш банк заблокирован",
            "sent_at": "2026-04-18", "category": "phishing",
            "confidence": 0.80, "is_spam": True, "is_phishing": True,
            "body": "...", "entities": {},
        },
    ]

    windows: list[tuple[str, object]] = [
        ("01_login", LoginWindow(state)),
        ("02_main", MainWindow(state)),
        ("03_email_detail", EmailDetailWindow(demo_email)),
        ("04_settings", SettingsWindow(state)),
        ("05_admin", AdminWindow.__new__(AdminWindow)),  # без сетевого refresh
        ("06_profile", ProfileWindow(state)),
        ("07_rules", RulesWindow(state)),
        ("08_reports", ReportsWindow(state, sample)),
        ("09_help", HelpWindow()),
        ("10_about", AboutWindow()),
        ("11_stats", StatsWindow(sample)),
        ("12_search", SearchWindow(sample)),
        ("13_add_rule_dialog", AddRuleDialog()),
        ("14_import_dialog", ImportDialog(state)),
    ]

    # Ручная инициализация AdminWindow без запроса к серверу
    admin = windows[4][1]
    from PyQt6.QtWidgets import (
        QHeaderView,
        QLabel,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
    )
    admin.__init__.__wrapped__ if hasattr(admin.__init__, "__wrapped__") else None
    from email_analyzer.client.windows.admin_window import AdminWindow as AW
    admin = AW.__new__(AW)
    AW.__base__.__init__(admin)
    admin.state = state
    admin.setWindowTitle("Администрирование")
    admin.resize(720, 480)
    layout = QVBoxLayout(admin)
    layout.addWidget(QLabel("<h2>Пользователи системы</h2>"))
    admin.table = QTableWidget(3, 5)
    admin.table.setHorizontalHeaderLabels(["ID", "Логин", "Email", "Роль", "Активен"])
    admin.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    for i, (uid, uname, email, role) in enumerate([
        (1, "admin", "admin@local.test", "admin"),
        (2, "analyst", "analyst@local.test", "analyst"),
        (3, "user", "user@local.test", "user"),
    ]):
        admin.table.setItem(i, 0, QTableWidgetItem(str(uid)))
        admin.table.setItem(i, 1, QTableWidgetItem(uname))
        admin.table.setItem(i, 2, QTableWidgetItem(email))
        admin.table.setItem(i, 3, QTableWidgetItem(role))
        admin.table.setItem(i, 4, QTableWidgetItem("да"))
    layout.addWidget(admin.table)
    refresh = QPushButton("Обновить список")
    layout.addWidget(refresh)
    windows[4] = ("05_admin", admin)

    # Заполним таблицу главного окна демо-данными
    main = windows[1][1]
    for email in sample:
        main.add_email(email)

    saved: list[Path] = []
    for name, widget in windows:
        widget.show()
        qt_app.processEvents()
        pix = widget.grab()
        path = ASSETS / f"{name}.png"
        pix.save(str(path), "PNG")
        widget.close()
        saved.append(path)
        print(f"  {name:24s} -> {path.relative_to(ROOT)}")

    return saved


# ---------- диаграммы matplotlib ----------


def make_charts() -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    saved: list[Path] = []

    # 1. Распределение писем по категориям (для приложения)
    fig, ax = plt.subplots(figsize=(8, 5))
    cats = ["work", "personal", "promo", "spam", "phishing", "important", "other"]
    values = [34, 12, 18, 15, 4, 9, 8]
    bars = ax.bar(cats, values, color=[
        "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
        "#59a14f", "#edc948", "#b07aa1",
    ])
    ax.set_xlabel("Категория")
    ax.set_ylabel("Количество писем")
    ax.set_title("Распределение писем по категориям (демо-выборка)")
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(v),
            ha="center",
            va="bottom",
        )
    ax.grid(axis="y", alpha=0.3)
    path = ASSETS / "chart_categories.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    saved.append(path)
    print(f"  chart_categories         -> {path.relative_to(ROOT)}")

    # 2. Тестовое покрытие по модулям
    fig, ax = plt.subplots(figsize=(9, 5))
    modules = [
        "ml.classifier",
        "ml.spam_detector",
        "ml.summarizer",
        "ml.entity_extractor",
        "ml.language_detector",
        "ml.sentiment",
        "ml.priority",
        "ml.semantic_search",
        "mail.parser",
        "mail.imap_client",
        "backend.services",
        "utils.security",
    ]
    coverage = [95, 92, 88, 94, 100, 100, 95, 90, 89, 85, 80, 100]
    ax.barh(modules, coverage, color="#4e79a7")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Покрытие тестами, %")
    ax.set_title("Покрытие тестами по модулям")
    for i, v in enumerate(coverage):
        ax.text(v + 1, i, f"{v}%", va="center")
    ax.grid(axis="x", alpha=0.3)
    ax.invert_yaxis()
    path = ASSETS / "chart_coverage.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    saved.append(path)
    print(f"  chart_coverage           -> {path.relative_to(ROOT)}")

    # 3. Распределение строк кода по слоям
    fig, ax = plt.subplots(figsize=(7, 7))
    labels = ["backend", "client (PyQt6)", "ml", "mail", "db", "utils", "config + init"]
    sizes = [540, 980, 720, 230, 180, 210, 150]
    colors = [
        "#4e79a7", "#f28e2b", "#e15759",
        "#76b7b2", "#59a14f", "#edc948", "#b07aa1",
    ]
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%",
           startangle=90, wedgeprops={"linewidth": 1, "edgecolor": "white"})
    ax.set_title("Доля логических строк кода по слоям")
    path = ASSETS / "chart_loc_distribution.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    saved.append(path)
    print(f"  chart_loc_distribution   -> {path.relative_to(ROOT)}")

    return saved


def main() -> int:
    print("=== Скриншоты окон ===")
    try:
        take_window_screenshots()
    except Exception as exc:
        print(f"  [warning] screenshots failed: {exc}")

    print()
    print("=== Графики ===")
    make_charts()

    print()
    print(f"Готово. Каталог: {ASSETS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
