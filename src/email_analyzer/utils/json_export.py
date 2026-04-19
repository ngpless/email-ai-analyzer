"""JSON-экспорт списка писем (для интеграций)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def _default(o: Any) -> Any:
    if isinstance(o, datetime):
        return o.isoformat()
    if hasattr(o, "value"):  # enums
        return o.value
    raise TypeError(f"Object of type {type(o).__name__} is not serializable")


def export_emails_to_json(
    emails: Iterable[dict],
    output_path: Path,
    pretty: bool = True,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = list(emails)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2 if pretty else None,
            default=_default,
        )
    return output_path
