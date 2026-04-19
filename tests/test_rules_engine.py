"""Тесты RulesEngine."""

from __future__ import annotations

from email_analyzer.backend.services.rules_engine import RulesEngine
from email_analyzer.db.models import Category, Rule


def _make_rule(
    name: str,
    pattern: str,
    field: str = "subject",
    action: Category | None = None,
    notify: bool = False,
) -> Rule:
    return Rule(
        owner_id=1,
        name=name,
        pattern=pattern,
        field=field,
        action_category=action,
        notify=notify,
    )


def test_no_rules_no_matches():
    engine = RulesEngine([])
    assert engine.apply("subject", "body", "sender@x.ru") == []


def test_subject_rule_matches_case_insensitive():
    rules = [_make_rule("Boss", "босс|шеф", action=Category.IMPORTANT)]
    matches = RulesEngine(rules).apply("Привет от Шефа", "", "")
    assert len(matches) == 1
    assert matches[0].rule_name == "Boss"


def test_sender_field_rule():
    rules = [_make_rule("BankAlerts", "@bank\\.", field="sender", notify=True)]
    matches = RulesEngine(rules).apply("", "", "alerts@bank.com")
    assert len(matches) == 1
    assert matches[0].notify is True


def test_no_match_for_unrelated_text():
    rules = [_make_rule("Bank", "банк", field="subject")]
    matches = RulesEngine(rules).apply("Встреча", "тело", "a@b.c")
    assert matches == []
