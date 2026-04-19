"""«О программе»."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from email_analyzer import __version__


ABOUT_TEXT = f"""
<h2>Email AI Analyzer</h2>
<p>Версия: <b>{__version__}</b></p>
<p>AI-приложение для анализа почтовых сообщений.</p>
<p>
    Работа выполнена в рамках <b>преддипломной практики и ВКР</b> в
    ЧОУВО «МУ им. С.Ю. Витте» (МУИВ).
</p>
<p>Направление: 09.03.03 Прикладная информатика<br>
Профиль: «Искусственный интеллект и анализ данных»</p>
<p>Автор: <b>Нефедов Алексей Геннадьевич</b><br>
№ студ.билета: 70200291</p>
<p>Руководитель: Коротков Дмитрий Павлович</p>
<p>Репозиторий: https://github.com/ngpless/email-ai-analyzer</p>
<p>2026 год.</p>
"""


class AboutWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("О программе")
        self.resize(380, 260)

        layout = QVBoxLayout(self)
        label = QLabel(ABOUT_TEXT)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
