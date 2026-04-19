"""CSV-экспорт списка писем."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


CSV_HEADERS = [
    "sender", "recipient", "subject", "sent_at",
    "category", "confidence", "is_spam", "is_phishing",
]


def export_emails_to_csv(emails: Iterable[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_HEADERS,
            extrasaction="ignore",
        )
        writer.writeheader()
        for email in emails:
            writer.writerow({k: email.get(k, "") for k in CSV_HEADERS})
    return output_path
