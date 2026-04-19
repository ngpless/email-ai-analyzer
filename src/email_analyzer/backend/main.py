"""Точка входа FastAPI.

Запуск: `uvicorn email_analyzer.backend.main:app --reload`
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from email_analyzer.backend.api import admin, analysis, auth, stats
from email_analyzer.config import get_settings
from email_analyzer.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(admin.router)
app.include_router(stats.router)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
def health() -> dict[str, object]:
    """Проверка работоспособности: статус, БД, версия, uptime."""
    from email_analyzer.db.session import get_engine

    db_ok = True
    try:
        engine = get_engine()
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "version": settings.app_version,
    }
