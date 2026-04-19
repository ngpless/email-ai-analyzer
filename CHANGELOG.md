# Журнал изменений

Все значимые изменения проекта — здесь. Формат [Keep a Changelog](https://keepachangelog.com/),
версионирование [SemVer](https://semver.org/).

## [Unreleased]

### Добавлено
- Собранный исполняемый файл `dist/EmailAIAnalyzer.exe` через PyInstaller 6.19
  (размер 125 МБ, включает Qt, scikit-learn, numpy — в Git не коммитится,
  прилагается к ZIP-сдаче).
- Генератор отчёта по преддипломной практике (`scripts/generate_report.py`),
  собирающий docx с титулом, главами, 51 листингом кода и 17 изображениями.
- Генератор ассетов (`scripts/generate_assets.py`) — 14 скриншотов окон
  в offscreen-режиме Qt + 3 графика matplotlib.
- CHANGELOG для отслеживания истории изменений.
- CI на GitHub Actions (pytest на Windows и Ubuntu, Python 3.11/3.12).
- Dockerfile и docker-compose.yml с PostgreSQL.
- Makefile для частых команд (install/test/cov/lint/run/build).
- CONTRIBUTING.md с правилами коммитов.
- LICENSE (educational).
- Pre-commit config (ruff + стандартные hooks).
- Ruff-конфигурация в pyproject.toml.
- `.env.example` со всеми настройками.
- `LanguageDetector` — определение языка (ru/en/mixed).
- `SentimentAnalyzer` — тональность письма.
- `PriorityScorer` — приоритет (critical/high/normal/low).
- `SemanticSearch` — семантический поиск по почте (TF-IDF + cosine).
- `LLMProvider` — абстракция для облачных LLM-провайдеров.
- `Attachment` — модель БД для метаданных вложений.
- `RulesEngine` — движок пользовательских regex-правил.
- `StatsService` и endpoint `/stats/compute`.
- CSV, JSON экспорты писем.
- `.mbox` импорт.
- `StatsWindow` и `SearchWindow` (GUI).
- CLI-утилита `python -m email_analyzer.cli analyze|version`.
- Встроенный логгер.
- Расширенный `/health` с проверкой БД.

## [0.1.0] — 2026-04-19

### Добавлено
- Каркас приложения (FastAPI backend + PyQt6 клиент).
- ML-ядро: классификатор, спам-детектор, суммаризатор, извлечение сущностей.
- IMAP-клиент (тонкая обёртка над `imaplib`) с FakeBackend для тестов.
- Роли пользователей: admin / analyst / user.
- Экспорт отчётов в .docx и .xlsx.
- 12 окон GUI.
- pytest-сьют: 49 тестов, полностью зелёные.
- Документация: архитектура, ТЗ (ГОСТ 34.602-2020), тест-план.
