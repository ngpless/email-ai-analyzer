"""Тесты CSV и JSON экспортов."""

from __future__ import annotations

import csv
import json

from email_analyzer.utils.csv_export import export_emails_to_csv
from email_analyzer.utils.json_export import export_emails_to_json


SAMPLE = [
    {
        "sender": "a@b.com",
        "subject": "Привет",
        "sent_at": "2026-04-19",
        "category": "work",
        "is_spam": False,
    },
    {
        "sender": "promo@shop.com",
        "subject": "Скидка 70%",
        "sent_at": "2026-04-18",
        "category": "promo",
        "is_spam": True,
    },
]


def test_csv_writes_header_and_rows(tmp_path):
    path = tmp_path / "emails.csv"
    export_emails_to_csv(SAMPLE, path)
    assert path.exists()
    with path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["sender"] == "a@b.com"
    assert rows[1]["is_spam"] == "True"


def test_json_writes_list(tmp_path):
    path = tmp_path / "emails.json"
    export_emails_to_json(SAMPLE, path)
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["subject"] == "Привет"


def test_json_handles_datetime(tmp_path):
    from datetime import datetime

    path = tmp_path / "with_dt.json"
    export_emails_to_json([{"sent_at": datetime(2026, 4, 19, 10, 0)}], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["sent_at"].startswith("2026-04-19")
