"""Тесты LLMProvider (через EchoLLMProvider)."""

from __future__ import annotations

from email_analyzer.ml.llm_provider import EchoLLMProvider


def test_summarize_returns_prefixed_text():
    provider = EchoLLMProvider()
    response = provider.summarize("Первое предложение.\nВторое предложение.")
    assert "echo-summary" in response.text
    assert response.model == "echo"
    assert response.tokens > 0


def test_draft_reply_style_embedded():
    response = EchoLLMProvider().draft_reply("Проверь почту", style="formal")
    assert "echo-reply/formal" in response.text
