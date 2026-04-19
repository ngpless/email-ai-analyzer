# Матрица фич

Сводная таблица реализованных возможностей по модулям.

## ML / AI

| Фича | Модуль | Тесты |
|---|---|---|
| Классификация писем | `ml.classifier.EmailClassifier` | ✅ |
| Спам/фишинг (эвристика) | `ml.spam_detector.SpamDetector` | ✅ |
| Экстрактивная суммаризация | `ml.summarizer.Summarizer` | ✅ |
| Извлечение сущностей | `ml.entity_extractor.EntityExtractor` | ✅ |
| Определение языка | `ml.language_detector.LanguageDetector` | ✅ |
| Тональность | `ml.sentiment.SentimentAnalyzer` | ✅ |
| Приоритет | `ml.priority.PriorityScorer` | ✅ |
| Поиск по смыслу | `ml.semantic_search.SemanticSearch` | ✅ |
| LLM-абстракция | `ml.llm_provider.LLMProvider` | ✅ |

## Backend (FastAPI)

| Endpoint | Назначение | Роль |
|---|---|---|
| `POST /auth/register` | Регистрация | все |
| `POST /auth/login` | Получение JWT | все |
| `GET /auth/me` | Профиль | auth |
| `POST /analyze/email` | Анализ одного письма | auth |
| `GET /admin/users` | Список пользователей | admin |
| `POST /admin/users/{id}/role` | Смена роли | admin |
| `POST /admin/users/{id}/deactivate` | Блокировка | admin |
| `POST /stats/compute` | Статистика по списку | auth |
| `GET /health` | Health-чек с DB-probe | public |

## Mail

- IMAP-клиент (`mail.imap_client.ImapClient`) + FakeBackend для тестов.
- MIME-парсер (`mail.parser.parse_email_bytes`) — plain + HTML.
- `.mbox` импорт (`mail.mbox_importer.import_mbox`).

## Экспорты

- `.docx` (`utils.reports.export_emails_to_docx`)
- `.xlsx` (`utils.reports.export_emails_to_xlsx`)
- `.csv` (`utils.csv_export.export_emails_to_csv`)
- `.json` (`utils.json_export.export_emails_to_json`)

## GUI (PyQt6, 14 окон)

1. LoginWindow
2. MainWindow
3. EmailDetailWindow
4. SettingsWindow (5 вкладок)
5. AdminWindow
6. ProfileWindow
7. RulesWindow
8. ReportsWindow
9. HelpWindow
10. AboutWindow
11. StatsWindow
12. SearchWindow
13. AddRuleDialog
14. ImportDialog

## DevOps

- GitHub Actions CI (`.github/workflows/tests.yml`).
- Dockerfile + docker-compose.yml (с PostgreSQL).
- Makefile (install, test, cov, lint, run-server, run-client, build-exe, clean).
- Pre-commit (ruff + стандартные hooks).
- `.env.example` — все конфигурируемые переменные.
