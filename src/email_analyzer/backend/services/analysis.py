"""Высокоуровневый сервис анализа писем.

Оркестрирует все ML-компоненты:
    - классификатор (TF-IDF / LogReg)
    - детектор спама и фишинга
    - суммаризатор
    - извлекатель сущностей

Работает в pure-функциональном стиле — не хранит состояние между
письмами, кроме обученной модели классификатора.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from email_analyzer.db.models import Category, Classification
from email_analyzer.ml import (
    EmailClassifier,
    EntityExtractor,
    SpamDetector,
    Summarizer,
)


@dataclass(frozen=True, slots=True)
class EmailAnalysis:
    category: Category
    confidence: float
    is_spam: bool
    is_phishing: bool
    spam_score: float
    summary: str
    entities: dict[str, list[str]]


class AnalysisService:
    def __init__(
        self,
        classifier: Optional[EmailClassifier] = None,
        spam_detector: Optional[SpamDetector] = None,
        summarizer: Optional[Summarizer] = None,
        entity_extractor: Optional[EntityExtractor] = None,
    ) -> None:
        self.classifier = classifier or EmailClassifier()
        if not self.classifier.is_fitted():
            self.classifier.fit_seed()
        self.spam_detector = spam_detector or SpamDetector()
        self.summarizer = summarizer or Summarizer(max_sentences=3)
        self.entity_extractor = entity_extractor or EntityExtractor()

    def analyze(
        self,
        subject: str,
        body: str,
        sender: str = "",
    ) -> EmailAnalysis:
        text = f"{subject}\n{body}"

        cls_result = self.classifier.predict(text)
        spam_result = self.spam_detector.detect(subject, body, sender=sender)

        category = cls_result.category
        # Если спам-детектор сработал уверенно — доверяем ему
        if spam_result.is_phishing and category != Category.PHISHING:
            category = Category.PHISHING
        elif spam_result.is_spam and category not in (Category.SPAM, Category.PHISHING):
            category = Category.SPAM

        summary = self.summarizer.summarize(body)
        entities = self.entity_extractor.extract(body).to_dict()

        return EmailAnalysis(
            category=category,
            confidence=cls_result.confidence,
            is_spam=spam_result.is_spam,
            is_phishing=spam_result.is_phishing,
            spam_score=spam_result.score,
            summary=summary,
            entities=entities,
        )

    def to_db_model(self, analysis: EmailAnalysis, email_id: int) -> Classification:
        return Classification(
            email_id=email_id,
            category=analysis.category,
            confidence=analysis.confidence,
            is_spam=analysis.is_spam,
            is_phishing=analysis.is_phishing,
            summary=analysis.summary,
            entities_json=json.dumps(analysis.entities, ensure_ascii=False),
        )
