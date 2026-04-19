"""Генерация прототипов (wireframes) интерфейса.

Прототип по методичке МУИВ — это грубый черновой эскиз окна с
плейсхолдерами: серые блоки вместо реальных данных, схематичные кнопки.
Макеты (финальные) уже есть — это скриншоты PyQt6-окон.

Автор: Нефедов А. Г.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "report_assets"
OUT.mkdir(parents=True, exist_ok=True)


def _frame(ax, x, y, w, h, text="", fill="#D8D8D8", border="#666",
           fontsize=9, text_color="#333", dashed=False):
    style = ":" if dashed else "-"
    rect = patches.Rectangle(
        (x, y), w, h, linewidth=1.0,
        edgecolor=border, facecolor=fill, linestyle=style,
    )
    ax.add_patch(rect)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fontsize, color=text_color)


def _text(ax, x, y, text, fontsize=10, color="#333", weight="normal"):
    ax.text(x, y, text, fontsize=fontsize, color=color, fontweight=weight)


def _lines(ax, x, y, count=3, width=3.0, gap=0.15, color="#AAA"):
    """Серые «полоски текста»."""
    for i in range(count):
        ax.add_patch(patches.Rectangle(
            (x, y - i * gap), width, gap * 0.5,
            facecolor=color, edgecolor="none",
        ))


def _base(title: str, figsize=(14, 9)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    return fig, ax


def _save(fig, name: str) -> None:
    path = OUT / name
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {path.relative_to(ROOT)}")


# ---------- Прототип: MainWindow ----------


def wireframe_main() -> None:
    fig, ax = _base("Прототип (wireframe) главного окна", figsize=(14, 8.5))

    # Внешняя рамка окна
    _frame(ax, 0.3, 0.3, 13.4, 8.0, fill="white", border="#222", dashed=False)

    # Строка меню
    for i, item in enumerate(["Файл", "Инструменты", "Пользователь", "Справка"]):
        _frame(ax, 0.5 + i * 1.5, 7.7, 1.4, 0.5, item, fill="#F0F0F0",
               border="#888", fontsize=9)

    # Тулбар
    for i, item in enumerate(["[ Импорт ]", "[ Настройки ]", "[ Отчёты ]"]):
        _frame(ax, 0.5 + i * 1.8, 7.0, 1.6, 0.5, item, fill="#E5E5E5",
               border="#777", fontsize=8)

    # Таблица писем
    _frame(ax, 0.5, 1.2, 13.0, 5.6, fill="#FAFAFA", border="#555")

    # Заголовки колонок
    headers = ["От", "Тема", "Дата", "Категория", "Спам?"]
    widths = [2.6, 4.6, 2.0, 2.2, 1.6]
    x = 0.5
    for i, (h, w) in enumerate(zip(headers, widths)):
        _frame(ax, x, 6.2, w, 0.6, h, fill="#E0E0E0", border="#555",
               fontsize=10)
        x += w

    # Строки-заглушки
    for row in range(7):
        y = 5.5 - row * 0.6
        x = 0.5
        for w in widths:
            _frame(ax, x + 0.1, y + 0.1, w - 0.2, 0.4,
                   fill="#EFEFEF", border="#CCC", fontsize=8)
            x += w

    # Подсказки стрелками (вынесены за границы рабочей области, чтобы
    # не накладываться на содержимое окна)
    ax.annotate("меню главных действий",
                xy=(3.0, 8.2), xytext=(8.5, 8.55), fontsize=9,
                color="#2E4C8A",
                arrowprops=dict(arrowstyle="->", color="#2E4C8A", lw=0.8))
    ax.annotate("панель инструментов — быстрые действия",
                xy=(3.2, 7.25), xytext=(7.5, 7.25), fontsize=9,
                color="#2E4C8A", va="center",
                arrowprops=dict(arrowstyle="->", color="#2E4C8A", lw=0.8))
    ax.annotate("таблица писем (сортировка по колонкам)",
                xy=(11.5, 3.0), xytext=(11.5, 0.05), fontsize=9,
                color="#2E4C8A", ha="center",
                arrowprops=dict(arrowstyle="->", color="#2E4C8A", lw=0.8))

    # Статус-бар
    _frame(ax, 0.5, 0.5, 13.0, 0.5, "статус: подключено, загружено 7",
           fill="#F5F5F5", border="#999", fontsize=9)

    _save(fig, "wireframe_main.png")


# ---------- Прототип: EmailDetailWindow ----------


def wireframe_email_detail() -> None:
    fig, ax = _base("Прототип (wireframe) окна просмотра письма",
                    figsize=(12, 9))
    ax.set_xlim(0, 12)

    _frame(ax, 0.3, 0.3, 11.4, 8.4, fill="white", border="#222")

    # Шапка — метаданные
    _text(ax, 0.6, 8.1, "От:", fontsize=9, weight="bold")
    _frame(ax, 1.3, 8.0, 9.0, 0.4, "[ адрес отправителя ]",
           fill="#EFEFEF", fontsize=8)

    _text(ax, 0.6, 7.5, "Тема:", fontsize=9, weight="bold")
    _frame(ax, 1.3, 7.4, 9.0, 0.4, "[ тема письма ]", fill="#EFEFEF", fontsize=8)

    _text(ax, 0.6, 6.9, "Категория:", fontsize=9, weight="bold")
    _frame(ax, 1.8, 6.8, 2.0, 0.4, "[ work ]", fill="#C8DCF0",
           border="#2E4C8A", fontsize=8)
    _frame(ax, 4.0, 6.8, 1.8, 0.4, "Спам: нет", fill="#BEE5C2",
           border="#3A8048", fontsize=8)
    _frame(ax, 6.0, 6.8, 2.2, 0.4, "Фишинг: нет", fill="#BEE5C2",
           border="#3A8048", fontsize=8)
    _frame(ax, 8.4, 6.8, 2.8, 0.4, "Уверенность: 0.86",
           fill="#FFF5D1", border="#A08820", fontsize=8)

    # Саммари
    _text(ax, 0.6, 6.3, "Саммари:", fontsize=9, weight="bold")
    _frame(ax, 0.6, 5.3, 10.8, 0.9, fill="#F8F8F8", border="#AAA")
    _lines(ax, 0.8, 6.0, count=3, width=10.4, gap=0.22)

    # Сущности
    _text(ax, 0.6, 4.9, "Извлечённые сущности:", fontsize=9, weight="bold")
    _frame(ax, 0.6, 3.4, 5.2, 1.4, fill="#F8F8F8", border="#AAA")
    _text(ax, 0.8, 4.55, "даты: [ 25.04.2026 ]", fontsize=8)
    _text(ax, 0.8, 4.25, "суммы: [ — ]", fontsize=8)
    _text(ax, 0.8, 3.95, "почта: [ — ]", fontsize=8)
    _text(ax, 0.8, 3.65, "задачи: [ прошу ознакомиться ]", fontsize=8)

    # Тело письма
    _text(ax, 6.0, 4.9, "Тело письма:", fontsize=9, weight="bold")
    _frame(ax, 6.0, 0.7, 5.4, 4.1, fill="#F8F8F8", border="#AAA")
    for i in range(12):
        _lines(ax, 6.2, 4.5 - i * 0.3, count=1, width=5.0, gap=0.2)

    # Кнопки внизу
    _frame(ax, 0.6, 0.7, 2.2, 0.55, "[ Закрыть ]",
           fill="#E5E5E5", border="#555", fontsize=9)
    _frame(ax, 3.0, 0.7, 2.2, 0.55, "[ Пометить прочт. ]",
           fill="#BEE5C2", border="#3A8048", fontsize=9)

    ax.annotate("результат ML-анализа",
                xy=(5.5, 6.9), xytext=(7.5, 7.8), fontsize=9,
                color="#2E4C8A",
                arrowprops=dict(arrowstyle="->", color="#2E4C8A", lw=0.8))

    _save(fig, "wireframe_email_detail.png")


# ---------- Прототип: ImportDialog ----------


def wireframe_import_dialog() -> None:
    fig, ax = _base("Прототип (wireframe) диалога импорта писем",
                    figsize=(9, 8))
    ax.set_xlim(0, 9)

    _frame(ax, 0.3, 0.3, 8.4, 7.4, fill="white", border="#222")

    ax.text(4.5, 7.3, "Импорт писем из IMAP", fontsize=11,
            fontweight="bold", ha="center", color="#222")

    # Поля формы
    fields = [
        ("IMAP-сервер:", "imap.gmail.com"),
        ("Порт:", "993"),
        ("Логин:", "[ ваш email ]"),
        ("Пароль:", "[ ********* ]"),
        ("Сколько писем:", "10"),
    ]
    for i, (label, placeholder) in enumerate(fields):
        y = 6.3 - i * 0.8
        _text(ax, 0.6, y + 0.2, label, fontsize=10)
        _frame(ax, 3.2, y, 5.0, 0.5, placeholder,
               fill="#FFFFFF", border="#888", fontsize=9, text_color="#888")

    # Чекбокс SSL
    _frame(ax, 3.2, 2.2, 0.4, 0.4, "✓", fill="#C8DCF0",
           border="#2E4C8A", fontsize=10)
    _text(ax, 3.8, 2.35, "Использовать SSL (рекомендуется)", fontsize=9)

    # Прогресс-бар
    _text(ax, 0.6, 1.5, "Прогресс загрузки:", fontsize=9, weight="bold")
    _frame(ax, 0.6, 1.0, 7.8, 0.35, fill="#F0F0F0", border="#888")
    _frame(ax, 0.6, 1.0, 2.6, 0.35, fill="#4CAF50", border="#2E7D32")

    # Кнопки
    _frame(ax, 5.0, 0.4, 1.6, 0.5, "[ Отмена ]",
           fill="#E5E5E5", border="#555", fontsize=9)
    _frame(ax, 6.8, 0.4, 1.4, 0.5, "[ OK ]",
           fill="#2E4C8A", border="#1F2E4C", fontsize=9,
           text_color="white")

    _save(fig, "wireframe_import_dialog.png")


# ---------- Макет (готовое окно — отсылка к скрину 02_main.png) ----------


def comparison_layout() -> None:
    """Сопоставление прототип ↔ макет (для отчёта)."""
    fig, ax = _base("Сопоставление: прототип → макет главного окна",
                    figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)

    # Заголовки панелей — выставлены по центру соответствующих панелей.
    ax.text(3.25, 6.55, "Прототип (wireframe)", fontsize=12, ha="center",
            fontweight="bold", color="#2E4C8A")
    ax.text(10.75, 6.55, "Макет (финальный UI)", fontsize=12, ha="center",
            fontweight="bold", color="#3A8048")

    # Левая панель — прототип (x=0.2..6.3, гэп 6.3..7.7, правая 7.7..13.8)
    _frame(ax, 0.2, 0.4, 6.1, 5.8, fill="white", border="#222")
    _frame(ax, 0.4, 5.8, 5.7, 0.3, fill="#F0F0F0", border="#888")
    _frame(ax, 0.4, 5.3, 5.7, 0.3, fill="#E5E5E5", border="#777")
    for row in range(6):
        _frame(ax, 0.4, 4.8 - row * 0.7, 5.7, 0.5, fill="#F8F8F8",
               border="#BBB")
    ax.text(3.25, 3.4, "серые\nплейсхолдеры", fontsize=10,
            color="#666", ha="center", va="center", style="italic")

    # Правая панель — макет
    _frame(ax, 7.7, 0.4, 6.1, 5.8, fill="#FFFFFF", border="#222")
    _frame(ax, 7.9, 5.8, 5.7, 0.3, fill="#F5F5F5", border="#666")
    _frame(ax, 7.9, 5.3, 5.7, 0.3, fill="#E8F0FE", border="#2E4C8A")

    # Мини-имитация таблицы с данными
    rows_data = [
        ("manager@", "Отчёт за квартал", "19.04", "work", "нет"),
        ("noreply@", "ВЫИГРАЛИ!!!", "18.04", "spam", "да"),
        ("sec@paypal-fake", "Ваш банк...", "18.04", "phishing", "да"),
    ]
    for i, row in enumerate(rows_data):
        y = 4.8 - i * 0.6
        x = 7.9
        for j, cell in enumerate(row):
            w = 1.14
            color = "#FFFFFF"
            if j == 3:  # категория
                color = {"work": "#C8DCF0", "spam": "#F5D9C1",
                         "phishing": "#F8D8D8"}.get(cell, "#FFF")
            _frame(ax, x, y, w, 0.5, cell, fill=color, border="#AAA",
                   fontsize=7)
            x += w

    # Стрелка в центральном зазоре между панелями
    ax.annotate("", xy=(7.6, 3.3), xytext=(6.4, 3.3),
                arrowprops=dict(arrowstyle="->", color="#B03030", lw=2))
    ax.text(7.0, 3.75, "реализация\nв PyQt6", ha="center", va="center",
            fontsize=9, color="#B03030", fontweight="bold")

    _save(fig, "wireframe_vs_mockup.png")


def main() -> int:
    print("Генерация прототипов…")
    wireframe_main()
    wireframe_email_detail()
    wireframe_import_dialog()
    comparison_layout()
    print("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
