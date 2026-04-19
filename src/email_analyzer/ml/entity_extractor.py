"""Извлечение сущностей из текста письма.

Автор: Нефедов А. Г. (студ. билет 70200291).
Тема ВКР: «Разработка AI-приложения для анализа почтовых сообщений».

Реализация на регулярных выражениях. От spaCy и natasha осознанно
отказался: они тянут 200–400 МБ моделей, а для целевого набора
сущностей (даты, суммы, контакты, короткие фразы-задачи) этого
достаточно. Побочный эффект — модуль стартует мгновенно и не требует
отдельной загрузки весов.

Распознаются:
    даты — ISO, точечный русский формат, словесный («10 мая»);
    время — hh:mm;
    суммы — рубли, доллары, евро;
    e-mail и URL — по стандартным шаблонам;
    телефоны — евро- и российские форматы с допустимыми разделителями;
    задачи — фразы, начинающиеся с «прошу», «необходимо», «сделай»…

Покрытие ~80% реальных деловых писем (оценка вручную, см. отчёт).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_URL = re.compile(r"https?://[^\s<>()\"']+")
RE_PHONE = re.compile(
    r"(?:\+?\d{1,3}[\s\-(]*)?(?:\d{3,4})[\s\-)]*\d{3}[\s\-]*\d{2,4}"
)
RE_DATE_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
RE_DATE_RU = re.compile(
    r"\b\d{1,2}\.\d{1,2}\.(?:\d{2}|\d{4})\b"
)
RE_DATE_WORD = re.compile(
    r"\b\d{1,2}\s+(?:янв(?:аря)?|фев(?:раля)?|март(?:а)?|апр(?:еля)?|"
    r"ма(?:я|рта)|июн(?:я)?|июл(?:я)?|авг(?:уста)?|сен(?:тября)?|"
    r"окт(?:ября)?|ноя(?:бря)?|дек(?:абря)?)",
    re.IGNORECASE,
)
RE_TIME = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")
RE_MONEY = re.compile(
    r"\b\d{1,3}(?:[ .,]\d{3})*(?:[.,]\d+)?\s*"
    r"(?:руб(?:лей|\.?)|₽|\$|USD|EUR|€)\b",
    re.IGNORECASE,
)
RE_TASK_VERBS = re.compile(
    r"\b(?:прошу|нужно|необходимо|требуется|просьба|сделай|подготовь|"
    r"отправь|согласуй|подпиши|проверь|ответь)\b[^.!?\n]*",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ExtractedEntities:
    emails: tuple[str, ...] = field(default_factory=tuple)
    urls: tuple[str, ...] = field(default_factory=tuple)
    phones: tuple[str, ...] = field(default_factory=tuple)
    dates: tuple[str, ...] = field(default_factory=tuple)
    times: tuple[str, ...] = field(default_factory=tuple)
    amounts: tuple[str, ...] = field(default_factory=tuple)
    tasks: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "emails": list(self.emails),
            "urls": list(self.urls),
            "phones": list(self.phones),
            "dates": list(self.dates),
            "times": list(self.times),
            "amounts": list(self.amounts),
            "tasks": list(self.tasks),
        }


class EntityExtractor:
    def extract(self, text: str) -> ExtractedEntities:
        if not text:
            return ExtractedEntities()

        emails = tuple(_unique(RE_EMAIL.findall(text)))
        urls = tuple(_unique(RE_URL.findall(text)))
        phones = tuple(_unique(m.strip() for m in RE_PHONE.findall(text) if _looks_like_phone(m)))
        dates = tuple(_unique(
            RE_DATE_ISO.findall(text)
            + RE_DATE_RU.findall(text)
            + [m.group(0) for m in RE_DATE_WORD.finditer(text)]
        ))
        times = tuple(_unique(RE_TIME.findall(text)))
        amounts = tuple(_unique(RE_MONEY.findall(text)))
        tasks = tuple(_unique(
            m.group(0).strip() for m in RE_TASK_VERBS.finditer(text)
        ))

        return ExtractedEntities(
            emails=emails,
            urls=urls,
            phones=phones,
            dates=dates,
            times=times,
            amounts=amounts,
            tasks=tasks,
        )


def _unique(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _looks_like_phone(s: str) -> bool:
    digits = sum(1 for c in s if c.isdigit())
    return digits >= 7
