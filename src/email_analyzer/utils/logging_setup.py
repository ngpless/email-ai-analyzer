"""Единая настройка логирования."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


DEFAULT_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def configure(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    fmt: str = DEFAULT_FORMAT,
) -> logging.Logger:
    """Настроить root-логгер и, если указан файл, — файловый handler."""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    formatter = logging.Formatter(fmt)
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    root.addHandler(stream)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_h = logging.FileHandler(log_file, encoding="utf-8")
        file_h.setFormatter(formatter)
        root.addHandler(file_h)

    return root


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
