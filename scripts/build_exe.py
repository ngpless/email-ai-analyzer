"""Сборка исполняемого .exe через PyInstaller.

Требование методички: «Обязательно должен быть сформирован исполняемый
*.exe файл». Собираем клиент PyQt6 в один файл.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "src" / "email_analyzer" / "client" / "main.py"
NAME = "EmailAIAnalyzer"


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={NAME}",
        "--paths",
        str(ROOT / "src"),
        str(ENTRY),
    ]
    print("Запуск:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print("Сборка завершилась с ошибкой", file=sys.stderr)
        return result.returncode
    print(f"\n.exe собран: dist/{NAME}.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
