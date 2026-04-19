"""Корневая точка входа проекта.

Запускает PyQt6-клиент. Требование Программы ГИА-2025 (раздел 3.5,
Приложение 8): `main.py` должен располагаться в корневом каталоге
git-репозитория.

Для запуска серверной части используйте
`python -m uvicorn email_analyzer.backend.main:app --app-dir src`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _bootstrap_path() -> None:
    src = Path(__file__).resolve().parent / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    _bootstrap_path()
    from email_analyzer.client.main import main as client_main
    return client_main()


if __name__ == "__main__":
    sys.exit(main())
