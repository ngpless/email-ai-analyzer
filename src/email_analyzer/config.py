"""Конфигурация приложения.

Берёт параметры из переменных окружения. Значения по умолчанию подходят
для локальной разработки: SQLite-файл в `data/app.db`, bind на 127.0.0.1.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    """Параметры приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Email AI Analyzer"
    app_version: str = "0.1.0"

    database_url: str = Field(
        default_factory=lambda: f"sqlite:///{DATA_DIR / 'app.db'}"
    )

    secret_key: str = "dev-secret-change-me-in-prod"
    access_token_ttl_minutes: int = 60 * 24

    imap_timeout_seconds: int = 30

    ml_model_path: Path = DATA_DIR / "classifier.joblib"
    ml_min_samples_to_train: int = 3

    api_host: str = "127.0.0.1"
    api_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
