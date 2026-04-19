# Как дорабатывать проект

## Окружение

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS

make install
make test
```

## Стиль кода

- Python 3.11+.
- Tab-size 4 пробела.
- Максимальная длина строки — 100 символов.
- Docstrings в формате «краткое описание + секция со списком».
- Типы через `typing` / PEP 585.

## Структура коммитов

Префиксы (Conventional Commits):

| Префикс | Когда использовать |
|---|---|
| `feat:` | Новая функциональность |
| `fix:` | Исправление бага |
| `docs:` | Только документация |
| `test:` | Добавление / исправление тестов |
| `refactor:` | Переработка без изменения поведения |
| `build:` | Зависимости / сборка / CI |
| `chore:` | Прочее (конфиги, гитигнор) |
| `perf:` | Оптимизация производительности |

## Перед коммитом

1. `make test` — все тесты должны быть зелёные.
2. `make lint` — без ошибок ruff.
3. Обновить `CHANGELOG.md` если изменения видимы пользователю.

## Добавление нового окна

1. Создать `src/email_analyzer/client/windows/my_window.py`.
2. Зарегистрировать в `windows/__init__.py` (добавить в `__all__`).
3. Добавить smoke-тест в `tests/test_client_imports.py`.
