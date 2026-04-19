"""Общие фикстуры: in-memory БД, тестовое FastAPI-приложение."""

from __future__ import annotations

from typing import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from email_analyzer.backend.api import admin, analysis, auth, stats
from email_analyzer.backend.deps import get_db
from email_analyzer.db.models import Base


@pytest.fixture
def test_engine():
    # StaticPool гарантирует, что все сессии используют одно и то же
    # in-memory SQLite-соединение; иначе каждая новая сессия получает
    # свою собственную пустую БД.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine) -> Iterator[Session]:
    factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def app_with_db(test_engine) -> FastAPI:
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(analysis.router)
    app.include_router(admin.router)
    app.include_router(stats.router)

    def _override_get_db() -> Iterator[Session]:
        factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return app


@pytest.fixture
def client(app_with_db: FastAPI) -> Iterator[TestClient]:
    with TestClient(app_with_db) as c:
        yield c
