"""Движок правил автоклассификации писем.

Применяет пользовательские regex-правила к теме/телу/отправителю и
возвращает сработавшие действия. Независим от ML — пересекается в
`AnalysisService.analyze()` как override.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from email_analyzer.db.models import Category, Rule


@dataclass(frozen=True, slots=True)
class RuleMatch:
    rule_name: str
    action_category: Category | None
    notify: bool


class RulesEngine:
    def __init__(self, rules: list[Rule]) -> None:
        self._compiled = [
            (rule, re.compile(rule.pattern, re.IGNORECASE))
            for rule in rules
        ]

    def apply(self, subject: str, body: str, sender: str) -> list[RuleMatch]:
        fields = {"subject": subject, "body": body, "sender": sender}
        matched: list[RuleMatch] = []
        for rule, pattern in self._compiled:
            target = fields.get(rule.field, "")
            if pattern.search(target):
                matched.append(RuleMatch(
                    rule_name=rule.name,
                    action_category=rule.action_category,
                    notify=rule.notify,
                ))
        return matched
