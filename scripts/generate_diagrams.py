"""Генерация проектных диаграмм через Graphviz.

Graphviz автоматически раскладывает графы, что гарантирует чистый вид
без перекрытий текста и пересечений стрелок. Для каждой диаграммы —
отдельная функция, возвращающая PNG в docs/report_assets/.

Каждая диаграмма соответствует требованиям методички ГИА-2025:
    - IDEF0 AS-IS / TO-BE — моделирование бизнес-процессов;
    - DFD первого уровня;
    - UML Use Case — роли и сценарии;
    - UML Activity — поток действий при импорте;
    - UML Sequence — план интеграции;
    - Диаграмма компонентов — архитектура;
    - Дерево функций;
    - Сценарий диалога;
    - ER-диаграмма (нотация Чена), уточнённая ER, схема БД;
    - Виды тестирования;
    - Виды развёртывания.
"""

from __future__ import annotations

import sys
from pathlib import Path

from graphviz import Digraph, Graph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "report_assets"
OUT.mkdir(parents=True, exist_ok=True)


# ---------- Хелперы ----------

FONT = "Arial"


def _save(dot, name: str) -> None:
    target = OUT / name
    dot.render(filename=target.with_suffix(""), format="png", cleanup=True)
    print(f"  -> {target.relative_to(ROOT)}")


def _base_digraph(rankdir: str = "LR") -> Digraph:
    g = Digraph(format="png")
    g.attr(
        rankdir=rankdir,
        fontname=FONT,
        bgcolor="white",
        pad="0.3",
        dpi="150",
    )
    g.attr("node", fontname=FONT, fontsize="11", margin="0.15,0.1")
    g.attr("edge", fontname=FONT, fontsize="10")
    return g


# ---------- 1. IDEF0 AS-IS ----------


def draw_idef0_as_is() -> None:
    g = _base_digraph("LR")
    g.attr(label="IDEF0 AS-IS — ручная обработка входящих писем",
           labelloc="t", fontsize="14")
    g.attr("node", shape="box", style="filled,rounded",
           fillcolor="#F5D9C1", color="#B37139", width="3", height="1.2")

    g.node("A0", "A0. Обработать\nвходящее письмо\n(вручную)")

    # Inputs
    g.node("in", "новое письмо\n(из IMAP)", shape="plaintext",
           fillcolor="white", style="")
    g.edge("in", "A0")

    # Outputs
    g.node("out", "прочитано /\nперемещено в папку",
           shape="plaintext", fillcolor="white", style="")
    g.edge("A0", "out")

    # Control (top)
    g.node("ctrl", "корпоративные\nполитики обработки",
           shape="plaintext", fillcolor="white", style="")
    g.edge("ctrl", "A0")

    # Mechanism (bottom)
    g.node("mech", "пользователь +\nпочтовый клиент",
           shape="plaintext", fillcolor="white", style="")
    g.edge("mech", "A0")

    _save(g, "diagram_idef0_as_is")


# ---------- 2. IDEF0 TO-BE ----------


def draw_idef0_to_be() -> None:
    g = _base_digraph("LR")
    g.attr(label="IDEF0 TO-BE — автоматизированный анализ",
           labelloc="t", fontsize="14")
    g.attr("node", shape="box", style="filled,rounded", width="2.4", height="1.0")

    g.node("A1", "A1. Загрузить\nписьма по IMAP",
           fillcolor="#C8DCF0", color="#2E4C8A")
    g.node("A2", "A2. ML-анализ\n(категория, спам,\nсаммари, сущности)",
           fillcolor="#BEE5C2", color="#3A8048")
    g.node("A3", "A3. Предъявить\nрезультат\nпользователю",
           fillcolor="#C8DCF0", color="#2E4C8A")

    g.edge("A1", "A2", label="текст письма")
    g.edge("A2", "A3", label="категория,\nсаммари, JSON")

    g.node("start", "IMAP-сервер", shape="plaintext", fillcolor="white", style="")
    g.node("end_", "пользователь\nпринимает решение",
           shape="plaintext", fillcolor="white", style="")
    g.edge("start", "A1")
    g.edge("A3", "end_")

    _save(g, "diagram_idef0_to_be")


# ---------- 3. DFD ----------


def draw_dfd() -> None:
    g = _base_digraph("LR")
    g.attr(label="DFD первого уровня (нотация Гейна-Сарсона)",
           labelloc="t", fontsize="14")

    # Внешние сущности — прямоугольники
    g.attr("node", shape="box", style="filled", fillcolor="#F5F5F5", color="#555")
    g.node("User", "Пользователь")
    g.node("Imap", "IMAP-сервер")

    # Процессы — скруглённые
    g.attr("node", shape="box", style="filled,rounded", fillcolor="#C8DCF0",
           color="#2E4C8A")
    g.node("P1", "1. Аутентификация\n(JWT)")
    g.node("P2", "2. Импорт писем\nиз IMAP")
    g.node("P3", "3. Анализ письма\n(ML-ядро)")
    g.node("P4", "4. Просмотр и\nсемантический поиск")
    g.node("P5", "5. Формирование\nотчёта .docx/.xlsx")

    # Хранилища — цилиндры
    g.attr("node", shape="cylinder", style="filled", fillcolor="#FFF5D1",
           color="#A08820")
    g.node("D1", "D1. users")
    g.node("D2", "D2. emails +\nclassifications")
    g.node("D3", "D3. rules + labels")
    g.node("D4", "D4. model.joblib")

    # Потоки данных
    g.edge("User", "P1", label="логин/пароль")
    g.edge("P1", "D1", label="проверка")
    g.edge("P1", "User", label="JWT токен")
    g.edge("User", "P2", label="параметры\nIMAP")
    g.edge("P2", "Imap", label="FETCH")
    g.edge("Imap", "P2", label="письма RFC822")
    g.edge("P2", "D2", label="запись")
    g.edge("P2", "P3", label="текст")
    g.edge("D4", "P3", label="модель")
    g.edge("P3", "D2", label="category,\nsummary")
    g.edge("D2", "P4", label="выборка")
    g.edge("D3", "P4", label="правила\nфильтрации")
    g.edge("D2", "P5", label="агрегация")
    g.edge("P5", "User", label=".docx/.xlsx")

    _save(g, "diagram_dfd")


# ---------- 4. Use Case ----------


def draw_use_case() -> None:
    g = _base_digraph("LR")
    g.attr(label="UML Use Case — роли и сценарии системы",
           labelloc="t", fontsize="14")

    # Акторы
    g.attr("node", shape="none", image="", style="")
    g.node("user", "👤\nuser", fontsize="11")
    g.node("analyst", "👤\nanalyst", fontsize="11")
    g.node("admin", "👤\nadmin", fontsize="11")
    g.node("imap", "🖥\nIMAP-сервер", fontsize="11")

    # Варианты использования — эллипсы в кластере
    with g.subgraph(name="cluster_sys") as c:
        c.attr(label="Email AI Analyzer", style="rounded", color="#2E4C8A",
               fontname=FONT, fontsize="13")
        c.attr("node", shape="ellipse", style="filled",
               fillcolor="#FFF5D1", color="#A08820")
        c.node("UC1", "Войти в систему")
        c.node("UC2", "Импортировать\nписьма")
        c.node("UC3", "Анализировать\nписьмо")
        c.node("UC4", "Экспортировать\nотчёт")
        c.node("UC5", "Управлять\nправилами")
        c.node("UC6", "Семантический\nпоиск")
        c.node("UC7", "Администрировать\nпользователей")

    # Связи акторов с UC
    for actor, ucs in [
        ("user", ["UC1", "UC2", "UC3", "UC4", "UC5", "UC6"]),
        ("analyst", ["UC1", "UC2", "UC3", "UC4", "UC6"]),
        ("admin", ["UC1", "UC7"]),
    ]:
        for uc in ucs:
            g.edge(actor, uc, arrowhead="none")

    g.edge("imap", "UC2", arrowhead="none", style="dashed")

    _save(g, "diagram_use_case")


# ---------- 5. UML Activity ----------


def draw_activity() -> None:
    g = _base_digraph("TB")
    g.attr(label="UML Activity — импорт и анализ пакета писем",
           labelloc="t", fontsize="14")

    # Start
    g.node("start", "", shape="circle", style="filled", fillcolor="#222",
           width="0.3", height="0.3")

    g.attr("node", shape="box", style="filled,rounded",
           fillcolor="#C8DCF0", color="#2E4C8A")
    g.node("A", "Ввести параметры\nIMAP-подключения")
    g.node("B", "Подключиться к\nпочтовому серверу")
    g.node("C", "Получить список UID\nпоследних N писем")
    g.node("D", "Для каждого UID\nFETCH RFC822")
    g.node("E", "POST /analyze/email\nдля каждого письма")
    g.node("F", "Получить JSON\nс результатами")
    g.node("G", "Обновить таблицу\nглавного окна")

    # Decision
    g.node("dec", "спам или\nфишинг?", shape="diamond",
           fillcolor="#FFF5D1", color="#A08820", style="filled")

    g.node("H1", "Пометить красным,\nдобавить в уведомления",
           fillcolor="#F5D9C1", color="#B03030")
    g.node("H2", "Пометить как обычное,\nобновить счётчики",
           fillcolor="#BEE5C2", color="#3A8048")

    # End
    g.node("end", "", shape="doublecircle", style="filled",
           fillcolor="#222", width="0.3")

    # Переходы
    g.edge("start", "A")
    g.edge("A", "B")
    g.edge("B", "C")
    g.edge("C", "D")
    g.edge("D", "E")
    g.edge("E", "F")
    g.edge("F", "dec")
    g.edge("dec", "H1", label="да")
    g.edge("dec", "H2", label="нет")
    g.edge("H1", "G")
    g.edge("H2", "G")
    g.edge("G", "end")

    _save(g, "diagram_activity")


# ---------- 6. UML Sequence ----------


def draw_sequence() -> None:
    """UML Sequence — через текстовое представление на PlantUML-подобной
    раскладке через Graphviz проблематично. Используем простой digraph."""
    g = _base_digraph("LR")
    g.attr(label="UML Sequence — план интеграции «клиент ↔ сервер ↔ IMAP»",
           labelloc="t", fontsize="14")

    # Колонки-акторы
    g.attr("node", shape="box", style="filled", fillcolor="#E9F1FC",
           color="#2E4C8A")
    actors = ["Пользователь", "PyQt-клиент", "FastAPI", "IMAP-сервер", "ML-ядро"]
    for a in actors:
        g.node(a)

    g.attr("edge", arrowsize="0.7")

    steps = [
        ("Пользователь", "PyQt-клиент", "1. Нажал «Импорт»"),
        ("PyQt-клиент", "FastAPI", "2. POST /auth/login"),
        ("FastAPI", "PyQt-клиент", "3. JWT-токен"),
        ("PyQt-клиент", "IMAP-сервер", "4. FETCH RFC822"),
        ("IMAP-сервер", "PyQt-клиент", "5. raw bytes письма"),
        ("PyQt-клиент", "FastAPI", "6. POST /analyze/email"),
        ("FastAPI", "ML-ядро", "7. analyze(subject, body)"),
        ("ML-ядро", "FastAPI", "8. category, spam, summary"),
        ("FastAPI", "PyQt-клиент", "9. JSON ответ"),
        ("PyQt-клиент", "Пользователь", "10. Строка в таблице"),
    ]
    for i, (a, b, lbl) in enumerate(steps):
        g.edge(a, b, label=lbl, weight=str(i + 1))

    _save(g, "diagram_sequence")


# ---------- 7. Диаграмма компонентов ----------


def draw_components() -> None:
    g = _base_digraph("LR")
    g.attr(label="Диаграмма компонентов — архитектура Email AI Analyzer",
           labelloc="t", fontsize="14")
    g.attr("node", shape="component", style="filled")

    # Клиент
    with g.subgraph(name="cluster_client") as c:
        c.attr(label="Клиент (PyQt6, .exe 125 МБ)", style="rounded,filled",
               fillcolor="#EDF3FB", color="#2E4C8A", fontname=FONT)
        c.node("MainWindow", fillcolor="white")
        c.node("AdminWindow", fillcolor="white")
        c.node("SettingsWindow", fillcolor="white")
        c.node("ApiClient", fillcolor="#FFF5D1")
        c.node("ImapClient", fillcolor="#FFF5D1")

    # Сервер
    with g.subgraph(name="cluster_srv") as c:
        c.attr(label="Backend (FastAPI + SQLAlchemy)", style="rounded,filled",
               fillcolor="#EAF5EC", color="#3A8048", fontname=FONT)
        c.node("AuthRouter", "auth router", fillcolor="white")
        c.node("AnalyzeRouter", "analyze router", fillcolor="white")
        c.node("AdminRouter", "admin+stats router", fillcolor="white")
        c.node("AnalysisService", fillcolor="#BEE5C2")
        c.node("UserService", fillcolor="#BEE5C2")
        c.node("Classifier", "ML: Classifier", fillcolor="#F5D9C1")
        c.node("SpamDetector", "ML: SpamDetector", fillcolor="#F5D9C1")
        c.node("Summarizer", "ML: Summarizer", fillcolor="#F5D9C1")

    # Внешние ресурсы
    g.attr("node", shape="cylinder", style="filled", fillcolor="#F8D8D8",
           color="#883333")
    g.node("DB", "PostgreSQL /\nSQLite\n(12 таблиц)")
    g.node("Model", "model.joblib")
    g.node("IMAP", "IMAP-сервер\n(Gmail, Яндекс, ...)")

    # Связи
    g.edge("ApiClient", "AuthRouter", label="HTTPS+JWT")
    g.edge("ApiClient", "AnalyzeRouter", label="HTTPS+JWT")
    g.edge("ApiClient", "AdminRouter", label="HTTPS+JWT")
    g.edge("ImapClient", "IMAP", label="IMAP+TLS")
    g.edge("AuthRouter", "UserService")
    g.edge("AnalyzeRouter", "AnalysisService")
    g.edge("AnalysisService", "Classifier")
    g.edge("AnalysisService", "SpamDetector")
    g.edge("AnalysisService", "Summarizer")
    g.edge("UserService", "DB", label="SQL")
    g.edge("AnalysisService", "DB", label="SQL")
    g.edge("Classifier", "Model", label="load/save")
    g.edge("MainWindow", "ApiClient", style="dashed")
    g.edge("MainWindow", "ImapClient", style="dashed")

    _save(g, "diagram_components")


# ---------- 8. Дерево функций ----------


def draw_function_tree() -> None:
    g = _base_digraph("TB")
    g.attr(label="Дерево функций приложения",
           labelloc="t", fontsize="14")
    g.attr("node", shape="box", style="filled,rounded",
           fillcolor="white", color="#2E4C8A")

    g.node("root", "Email AI Analyzer", fillcolor="#2E4C8A",
           fontcolor="white", fontsize="13")
    g.node("grp1", "Клиентские функции", fillcolor="#BEE5C2")
    g.node("grp2", "Аналитические функции", fillcolor="#FFF5D1")
    g.node("grp3", "Служебные функции (admin)", fillcolor="#F5D9C1")

    g.edge("root", "grp1")
    g.edge("root", "grp2")
    g.edge("root", "grp3")

    # Листья группы 1
    for i, leaf in enumerate([
        "Вход (Login)", "Импорт писем IMAP",
        "Просмотр списка", "Детальный просмотр письма",
        "Личный кабинет", "Встроенная справка",
    ]):
        node_id = f"c1_{i}"
        g.node(node_id, leaf)
        g.edge("grp1", node_id)

    # Листья группы 2
    for i, leaf in enumerate([
        "Классификация (7 категорий)",
        "Детекция спама / фишинга",
        "Суммаризация текста",
        "Извлечение сущностей",
        "Семантический поиск",
        "Статистика по почте",
        "Пользовательские правила",
        "Экспорт .docx/.xlsx/.csv/.json",
    ]):
        node_id = f"c2_{i}"
        g.node(node_id, leaf)
        g.edge("grp2", node_id)

    # Листья группы 3
    for i, leaf in enumerate([
        "Управление пользователями",
        "Смена ролей",
        "Блокировка учёток",
        "Просмотр журнала аудита",
        "Переобучение модели",
    ]):
        node_id = f"c3_{i}"
        g.node(node_id, leaf)
        g.edge("grp3", node_id)

    _save(g, "diagram_function_tree")


# ---------- 9. Сценарий диалога ----------


def draw_dialog_scenario() -> None:
    g = _base_digraph("TB")
    g.attr(label="Сценарий диалога пользователя с приложением",
           labelloc="t", fontsize="14")
    g.attr("node", shape="box", style="filled,rounded")

    g.node("start", "Заставка входа", fillcolor="#C8DCF0", color="#2E4C8A")
    g.node("login", "Окно логина (Login)", fillcolor="#C8DCF0", color="#2E4C8A")
    g.node("main", "Главное окно\nсо списком писем",
           fillcolor="#BEE5C2", color="#3A8048")

    g.node("import", "Импорт писем\n(диалог IMAP)", fillcolor="#FFF5D1")
    g.node("detail", "Детальный просмотр\nписьма", fillcolor="#FFF5D1")
    g.node("settings", "Настройки (5 вкладок)", fillcolor="#FFF5D1")
    g.node("rules", "Правила\n(+диалог Add Rule)", fillcolor="#FFF5D1")
    g.node("reports", "Отчёты (.docx/.xlsx)", fillcolor="#FFF5D1")
    g.node("search", "Семантический поиск", fillcolor="#FFF5D1")
    g.node("stats", "Статистика", fillcolor="#FFF5D1")
    g.node("profile", "Личный кабинет", fillcolor="white")
    g.node("admin", "Админ-панель\n(если роль admin)",
           fillcolor="#F5D9C1", color="#B03030")
    g.node("help", "Справка + О программе", fillcolor="white")

    g.node("exit", "Выход из системы",
           fillcolor="#FFFFFF", shape="doublecircle")

    g.edge("start", "login")
    g.edge("login", "main", label="JWT получен")
    for target in ("import", "detail", "settings", "rules", "reports",
                   "search", "stats", "profile", "admin", "help"):
        g.edge("main", target)
        g.edge(target, "main", style="dashed", label="закрыть", fontsize="8")
    g.edge("main", "exit")

    _save(g, "diagram_dialog_scenario")


# ---------- 10. ER-диаграмма (Чен) ----------


def draw_er_basic() -> None:
    g = _base_digraph("LR")
    g.attr(label="ER-диаграмма (базовая, нотация Чена)",
           labelloc="t", fontsize="14")

    g.attr("node", shape="box", style="filled", fillcolor="white",
           color="#2E4C8A", fontsize="11")
    for entity in ("User", "EmailMessage", "Classification", "Attachment",
                   "Label", "Rule", "AnalysisReport", "Notification",
                   "EmailThread", "ImapAccount", "AuditLogEntry",
                   "TrainingSample"):
        g.node(entity)

    g.attr("node", shape="diamond", style="filled",
           fillcolor="#FFF5D1", color="#A08820", fontsize="10")
    relations = [
        ("owns", "User", "EmailMessage", "1", "N"),
        ("analyzed", "EmailMessage", "Classification", "1", "1"),
        ("has", "EmailMessage", "Attachment", "1", "N"),
        ("tagged", "EmailMessage", "Label", "M", "N"),
        ("applies", "User", "Rule", "1", "N"),
        ("generates", "User", "AnalysisReport", "1", "N"),
        ("receives", "User", "Notification", "1", "N"),
        ("groups", "EmailMessage", "EmailThread", "N", "1"),
        ("configures", "User", "ImapAccount", "1", "N"),
        ("produces", "User", "AuditLogEntry", "1", "N"),
        ("contributes", "User", "TrainingSample", "1", "N"),
    ]
    for rel, a, b, left_card, right_card in relations:
        rel_id = f"r_{rel}"
        g.node(rel_id, rel)
        g.edge(a, rel_id, label=left_card, arrowhead="none")
        g.edge(rel_id, b, label=right_card, arrowhead="none")

    _save(g, "diagram_er_basic")


# ---------- 11. Уточнённая ER (атрибуты) ----------


def draw_er_refined() -> None:
    g = _base_digraph("TB")
    g.attr(label="Уточнённая ER-диаграмма (с атрибутами)",
           labelloc="t", fontsize="14")

    # Сущности
    g.attr("node", shape="box", style="filled", fillcolor="white",
           color="#2E4C8A")
    g.node("User")
    g.node("EmailMessage")

    # Связь
    g.attr("node", shape="diamond", style="filled",
           fillcolor="#FFF5D1", color="#A08820")
    g.node("owns_rel", "owns")
    g.edge("User", "owns_rel", label="1", arrowhead="none")
    g.edge("owns_rel", "EmailMessage", label="N", arrowhead="none")

    # Атрибуты User — эллипсы
    g.attr("node", shape="ellipse", style="filled",
           fillcolor="white", color="#555", fontsize="9.5")
    user_attrs = [
        ("u_id", "id (PK)"), ("u_uname", "username (UQ)"),
        ("u_email", "email (UQ)"), ("u_pass", "password_hash"),
        ("u_role", "role"), ("u_active", "is_active"),
        ("u_name", "full_name"),
    ]
    for node_id, label in user_attrs:
        g.node(node_id, label)
        g.edge("User", node_id, arrowhead="none")

    email_attrs = [
        ("e_id", "id (PK)"), ("e_mid", "message_id"),
        ("e_from", "sender"), ("e_to", "recipient"),
        ("e_subj", "subject"), ("e_body", "body"),
        ("e_sent", "sent_at"), ("e_read", "is_read"),
    ]
    for node_id, label in email_attrs:
        g.node(node_id, label)
        g.edge("EmailMessage", node_id, arrowhead="none")

    _save(g, "diagram_er_refined")


# ---------- 12. Схема БД (физическая) ----------


def draw_schema_db() -> None:
    g = _base_digraph("LR")
    g.attr(label="Схема базы данных (физическое представление, 12 таблиц)",
           labelloc="t", fontsize="14")
    g.attr("node", shape="plain", fontname=FONT)

    def _table(name: str, cols: list[tuple[str, str]]) -> str:
        rows = "".join(
            f'<tr><td align="left" port="{c}"><b>{c}</b></td>'
            f'<td align="left">{t}</td></tr>'
            for c, t in cols
        )
        return (
            f'<<table border="0" cellborder="1" cellspacing="0">'
            f'<tr><td colspan="2" bgcolor="#2E4C8A">'
            f'<font color="white"><b>{name}</b></font></td></tr>'
            f"{rows}</table>>"
        )

    tables = {
        "users": [("id", "PK"), ("username", "UQ"), ("email", "UQ"),
                  ("password_hash", ""), ("role", ""), ("is_active", "")],
        "emails": [("id", "PK"), ("owner_id", "FK"), ("message_id", ""),
                   ("sender", ""), ("subject", ""), ("body", ""),
                   ("sent_at", "")],
        "classifications": [("id", "PK"), ("email_id", "FK"),
                            ("category", ""), ("confidence", ""),
                            ("is_spam", ""), ("summary", "")],
        "attachments": [("id", "PK"), ("email_id", "FK"),
                        ("filename", ""), ("mime_type", ""), ("size", "")],
        "rules": [("id", "PK"), ("owner_id", "FK"), ("name", ""),
                  ("pattern", ""), ("field", ""), ("action_category", "")],
        "labels": [("id", "PK"), ("owner_id", "FK"), ("name", ""), ("color", "")],
        "email_labels": [("id", "PK"), ("email_id", "FK"), ("label_id", "FK")],
        "threads": [("id", "PK"), ("owner_id", "FK"),
                    ("subject_normalized", ""), ("last_message_at", "")],
        "imap_accounts": [("id", "PK"), ("owner_id", "FK"), ("host", ""),
                          ("port", ""), ("username", "")],
        "audit_log": [("id", "PK"), ("user_id", "FK"), ("action", ""),
                      ("details", ""), ("ip_address", "")],
        "notifications": [("id", "PK"), ("user_id", "FK"), ("kind", ""),
                          ("message", ""), ("is_read", "")],
        "reports": [("id", "PK"), ("owner_id", "FK"),
                    ("title", ""), ("path", ""), ("format", "")],
    }
    for name, cols in tables.items():
        g.node(name, label=_table(name, cols))

    edges = [
        ("users:id", "emails:owner_id"),
        ("users:id", "rules:owner_id"),
        ("users:id", "labels:owner_id"),
        ("users:id", "threads:owner_id"),
        ("users:id", "imap_accounts:owner_id"),
        ("users:id", "audit_log:user_id"),
        ("users:id", "notifications:user_id"),
        ("users:id", "reports:owner_id"),
        ("emails:id", "classifications:email_id"),
        ("emails:id", "attachments:email_id"),
        ("emails:id", "email_labels:email_id"),
        ("labels:id", "email_labels:label_id"),
    ]
    for a, b in edges:
        g.edge(a, b, arrowhead="crow", arrowtail="none", dir="both")

    _save(g, "diagram_schema_db")


# ---------- 13. Виды тестирования ----------


def draw_testing_types() -> None:
    g = _base_digraph("TB")
    g.attr(label="Классификация видов тестирования",
           labelloc="t", fontsize="14")
    g.attr("node", shape="box", style="filled,rounded")

    g.node("root", "Виды тестирования", fillcolor="#2E4C8A",
           fontcolor="white", fontsize="13")

    groups = {
        "grp1": ("По доступу к коду",
                 ["Чёрный ящик (black box)", "Серый ящик (grey box)",
                  "Белый ящик (white box)"], "#C8DCF0"),
        "grp2": ("По объекту",
                 ["Функциональное", "Производительное", "Безопасности",
                  "Usability / UX", "Совместимости"], "#BEE5C2"),
        "grp3": ("По уровню",
                 ["Модульное (unit)", "Интеграционное", "Системное (E2E)"],
                 "#FFF5D1"),
        "grp4": ("По автоматизации",
                 ["Ручное", "Автоматизированное", "Полуавтоматическое"],
                 "#F5D9C1"),
        "grp5": ("По времени",
                 ["Smoke", "Регрессионное", "Приёмочное"], "#FADBD8"),
    }
    for key, (title, leaves, color) in groups.items():
        g.node(key, title, fillcolor=color)
        g.edge("root", key)
        for i, leaf in enumerate(leaves):
            leaf_id = f"{key}_{i}"
            g.node(leaf_id, leaf, fillcolor="white")
            g.edge(key, leaf_id)

    _save(g, "diagram_testing_types")


# ---------- 14. Виды развёртывания ----------


def draw_deployment_types() -> None:
    g = _base_digraph("TB")
    g.attr(label="Виды (стратегии) развёртывания ПО",
           labelloc="t", fontsize="14")
    g.attr("node", shape="ellipse", style="filled", fontsize="11")

    g.node("root", "Виды\nразвёртывания", fillcolor="#2E4C8A",
           fontcolor="white", fontsize="12")

    strategies = [
        ("s1", "Непрерывная\nинтеграция (CI)", "#BEE5C2"),
        ("s2", "Непрерывная\nдоставка (CD)", "#BEE5C2"),
        ("s3", "Непрерывное\nразвёртывание", "#BEE5C2"),
        ("s4", "Последовательное\n(rolling)", "#C8DCF0"),
        ("s5", "Сине-зелёный\n(blue-green)", "#C8DCF0"),
        ("s6", "Канареечный\nрелиз (canary)", "#FFF5D1"),
        ("s7", "A/B-тестирование", "#FFF5D1"),
        ("s8", "Повторное создание\n(recreate)", "#F5D9C1"),
        ("s9", "Скрытое развёртывание\n(shadow)", "#F5D9C1"),
    ]
    for node_id, label, color in strategies:
        g.node(node_id, label, fillcolor=color)
        g.edge("root", node_id, arrowhead="none")

    _save(g, "diagram_deployment_types")


# ---------- main ----------


def main() -> int:
    print("Генерация диаграмм через Graphviz…")
    draw_idef0_as_is()
    draw_idef0_to_be()
    draw_dfd()
    draw_use_case()
    draw_activity()
    draw_sequence()
    draw_components()
    draw_function_tree()
    draw_dialog_scenario()
    draw_er_basic()
    draw_er_refined()
    draw_schema_db()
    draw_testing_types()
    draw_deployment_types()
    print("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
