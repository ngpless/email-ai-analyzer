"""Абстрактный LLM-провайдер для опциональной замены локальных моделей.

Позволяет в отчёте / настройках выбрать реальный облачный LLM (OpenAI /
YandexGPT / GigaChat), не меняя код потребителей. В базовой поставке
подключён только `EchoLLMProvider`, который возвращает осмысленный
вывод без сетевых вызовов.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LLMResponse:
    text: str
    model: str
    tokens: int


class LLMProvider(ABC):
    """Интерфейс, которому должны соответствовать все провайдеры."""

    @abstractmethod
    def summarize(self, text: str, max_tokens: int = 256) -> LLMResponse: ...

    @abstractmethod
    def draft_reply(self, incoming: str, style: str = "neutral") -> LLMResponse: ...


class EchoLLMProvider(LLMProvider):
    """Офлайн-заглушка для тестов и дефолтной конфигурации."""

    def summarize(self, text: str, max_tokens: int = 256) -> LLMResponse:
        head = text.strip().splitlines()[:2]
        return LLMResponse(
            text="[echo-summary] " + " ".join(head)[:max_tokens],
            model="echo",
            tokens=min(len(text), max_tokens),
        )

    def draft_reply(self, incoming: str, style: str = "neutral") -> LLMResponse:
        return LLMResponse(
            text=f"[echo-reply/{style}] Получил ваше сообщение, отвечу позже.",
            model="echo",
            tokens=10,
        )
