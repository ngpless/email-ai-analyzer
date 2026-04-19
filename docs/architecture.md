# Архитектура приложения

## Общая схема

Приложение построено по **клиент-серверной** архитектуре — это соответствует
требованиям методички МУИВ («в качестве приоритетного решения следует
рассматривать программное обеспечение, построенное с использованием
клиент-серверной архитектуры»).

```
┌─────────────────────┐  HTTPS+JWT   ┌─────────────────────┐
│  PyQt6-клиент       │◄─────────────►│  FastAPI-backend    │
│  (12 окон,          │               │  (auth, analyze,    │
│  .exe через         │               │   admin)            │
│  PyInstaller)       │               │                     │
└─────────────────────┘               └──────────┬──────────┘
                                                 │ SQLAlchemy
                                                 ▼
                          ┌────────────────────────────────────┐
                          │  PostgreSQL (prod) / SQLite (dev)  │
                          │  таблицы: users, emails,           │
                          │  classifications, rules, reports   │
                          └────────────────────────────────────┘

                                                 ▲ читает IMAP
                                                 │
┌─────────────────────┐       IMAP+SSL           │
│  Почтовый сервер    │◄─────────────────────────┘
│  (Gmail/Yandex/…)   │
└─────────────────────┘

                          ┌────────────────────────────────────┐
                          │  ML-ядро (внутри backend)          │
                          │  - Classifier (TF-IDF+LogReg)      │
                          │  - SpamDetector (heuristics)       │
                          │  - Summarizer (extractive)         │
                          │  - EntityExtractor (regex)         │
                          └────────────────────────────────────┘
```

## Компоненты

### Клиент (`src/email_analyzer/client/`)

| Окно | Назначение |
|---|---|
| `LoginWindow` | Авторизация |
| `MainWindow` | Главное окно — список писем + меню/тулбар |
| `EmailDetailWindow` | Просмотр письма и результата анализа |
| `SettingsWindow` | 5 вкладок настроек (IMAP, ML, категории, уведомления, экспорт) |
| `AdminWindow` | Управление пользователями (только для admin) |
| `ProfileWindow` | Личный кабинет |
| `RulesWindow` | Пользовательские правила |
| `ReportsWindow` | Экспорт в .docx / .xlsx |
| `HelpWindow` | Встроенная справка |
| `AboutWindow` | О программе |
| `AddRuleDialog` | Диалог ввода нового правила |
| `ImportDialog` | Диалог импорта писем из IMAP |

Общение с сервером — через `ApiClient` (`requests`).

### Backend (`src/email_analyzer/backend/`)

- `main.py` — FastAPI-приложение.
- `api/auth.py` — `/auth/register`, `/auth/login`, `/auth/me`.
- `api/analysis.py` — `/analyze/email` (требует JWT).
- `api/admin.py` — `/admin/users*` (только admin).
- `services/analysis.py` — оркестрация ML-компонентов.
- `services/users.py` — CRUD пользователей, bcrypt, JWT.
- `deps.py` — DI-зависимости FastAPI.
- `schemas.py` — Pydantic v2 DTO.

### ML-ядро (`src/email_analyzer/ml/`)

- `classifier.py` — TF-IDF + LogReg, seed-набор данных (RU + EN), save/load через `joblib`.
- `spam_detector.py` — набор эвристик (ключевые слова, капс-lock, поддельные отправители).
- `summarizer.py` — экстрактивная суммаризация на TF-IDF.
- `entity_extractor.py` — извлечение дат/сумм/почты/телефонов/URL/задач регулярками.
- `language_detector.py` — определение языка (ru/en/mixed) по соотношению алфавитов.
- `sentiment.py` — тональность (positive/neutral/negative) на лексиконе.
- `priority.py` — приоритет письма (critical/high/normal/low).
- `semantic_search.py` — поиск по смыслу (TF-IDF + cosine similarity).
- `llm_provider.py` — абстракция LLM-провайдера для замены локальных моделей.

Все компоненты имеют общий стиль: чистые функции/методы, входные типы явные, результат — immutable `dataclass(frozen=True, slots=True)`.

### Mail (`src/email_analyzer/mail/`)

- `imap_client.py` — тонкая обёртка над `imaplib` с абстрактным бэкендом (для тестов без сети).
- `parser.py` — разбор MIME в `ParsedEmail` (работает на сырых байтах, полностью тестируется без сервера).

### DB (`src/email_analyzer/db/`)

- `models.py` — SQLAlchemy 2.x-модели (`DeclarativeBase`, `Mapped`).
- `session.py` — `Engine`/`sessionmaker`, поддерживает и SQLite, и PostgreSQL по одному URL.

## Безопасность

- Пароли: `bcrypt` напрямую (без passlib, из-за известной несовместимости с bcrypt 4.x).
- Токены: JWT (HS256) через `python-jose`.
- Роли: `admin`/`analyst`/`user` (требование ≥ 3 ролей).
- `require_admin` — FastAPI-зависимость, 403 если роль не admin.

## Расширяемость

- Заменить TF-IDF-классификатор на BERT: достаточно реализовать
  класс с методами `fit_seed()`, `is_fitted()`, `predict()`.
- Подключить LLM-суммаризатор (OpenAI/YandexGPT): тот же паттерн.
- Сменить БД на PostgreSQL: изменить только `DATABASE_URL` в `.env`.
