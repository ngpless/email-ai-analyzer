"""Управление сессией БД.

Поддерживаются SQLite (для разработки/тестов) и PostgreSQL
(для продакшена) через одну и ту же SQLAlchemy-модель.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from email_analyzer.config import DATA_DIR, get_settings
from email_analyzer.db.models import Base


_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker[Session]] = None


def get_engine(database_url: Optional[str] = None) -> Engine:
    """Вернуть (и при первом вызове — создать) SQLAlchemy-Engine.

    Для SQLite включена поддержка foreign_keys.
    """
    global _engine, _SessionFactory
    if _engine is not None and database_url is None:
        return _engine

    url = database_url or get_settings().database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, future=True)

    if url.startswith("sqlite") and "///" in url:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if database_url is None:
        _engine = engine
        _SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine


def init_db(database_url: Optional[str] = None) -> Engine:
    """Создать все таблицы."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


@contextmanager
def get_session() -> Iterator[Session]:
    """Контекстный менеджер сессии с автокоммитом при выходе без ошибок."""
    if _SessionFactory is None:
        get_engine()
    assert _SessionFactory is not None
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
