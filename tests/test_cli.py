"""Тесты CLI-утилиты."""

from __future__ import annotations

import json

from email_analyzer.cli import main


def test_cli_version(capsys):
    rc = main(["version"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out  # какая-то версия выведена


def test_cli_analyze_json_output(capsys):
    rc = main([
        "analyze",
        "--subject", "Встреча",
        "--body", "Коллеги, совещание в 10:00.",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "category" in data
    assert "confidence" in data
    assert isinstance(data["entities"], dict)
