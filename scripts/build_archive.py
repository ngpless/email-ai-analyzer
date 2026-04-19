"""Сборка ZIP-архива для сдачи практики.

Включаются: исходный код (src/), тесты, скрипты, документация, данные,
отчёт PDF/DOCX, презентация PPTX, исполняемый файл, файлы сборки
и конфигурации. Исключаются: виртуальное окружение, кэши, вложенные
zip-архивы, временные файлы.

Результат — ZIP на Рабочем столе с именем ФИО.zip.

Автор: Нефедов А. Г.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path.home() / "Desktop" / f"{ROOT.name}.zip"

SKIP_DIRS = {
    ".venv", "build", ".pytest_cache", "__pycache__", ".ruff_cache",
    "node_modules", ".idea", ".vscode", ".mypy_cache",
}

SKIP_FILES = {".coverage", "*.pyc", "*.pyo"}


def _should_skip(p: Path) -> bool:
    parts = set(p.parts)
    if parts & SKIP_DIRS:
        return True
    if p.suffix in {".pyc", ".pyo"}:
        return True
    if p.name == ".coverage":
        return True
    # Ранее случайно попавший во вложение старый zip — безусловно
    # исключаем по расширению.
    if p.suffix == ".zip":
        return True
    return False


def main() -> int:
    if not ROOT.exists():
        print(f"Не найден каталог проекта: {ROOT}", file=sys.stderr)
        return 1

    files: list[Path] = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not _should_skip(p.relative_to(ROOT)):
            files.append(p)

    files.sort()
    total = sum(f.stat().st_size for f in files)
    print(f"Файлов: {len(files)}, суммарный размер: {total / 1024 / 1024:.1f} МБ")
    print(f"Архив: {ARCHIVE}")

    if ARCHIVE.exists():
        ARCHIVE.unlink()

    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zf:
        for f in files:
            arcname = Path(ROOT.name) / f.relative_to(ROOT)
            zf.write(f, arcname=str(arcname))

    size = ARCHIVE.stat().st_size
    print(f"Готово: {size / 1024 / 1024:.1f} МБ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
