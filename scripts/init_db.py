"""Инициализация БД + seed-пользователей.

Запуск: `python scripts/init_db.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

# Добавляем src в sys.path, чтобы работало без установки пакета.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from email_analyzer.backend.services.users import UserService
from email_analyzer.db.models import Role
from email_analyzer.db.session import get_engine, init_db
from sqlalchemy.orm import sessionmaker


SEED_USERS = [
    ("admin", "admin@local.test", "admin123", Role.ADMIN, "Администратор"),
    ("analyst", "analyst@local.test", "analyst123", Role.ANALYST, "Аналитик"),
    ("user", "user@local.test", "user123", Role.USER, "Обычный пользователь"),
]


def main() -> int:
    init_db()
    engine = get_engine()
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = factory()
    try:
        service = UserService(db)
        for username, email, password, role, full_name in SEED_USERS:
            if service.get_by_username(username) is not None:
                print(f"skip: {username} уже существует")
                continue
            service.create(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                role=role,
            )
            print(f"created: {username} (role={role.value})")
        db.commit()
    finally:
        db.close()
    print("БД инициализирована.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
