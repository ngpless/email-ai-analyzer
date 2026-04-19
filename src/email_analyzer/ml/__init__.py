"""ML-ядро приложения.

Содержит:
    classifier        — классификация писем по категориям (TF-IDF + LogReg);
    spam_detector     — эвристический детектор спама и фишинга;
    summarizer        — экстрактивная суммаризация писем;
    entity_extractor  — извлечение дат/сумм/контактов/задач;
    language_detector — определение языка (ru/en/mixed);
    sentiment         — анализ тональности;
    priority          — оценка приоритета письма;
    semantic_search   — поиск по смыслу (TF-IDF + cosine).

Все компоненты следуют единому интерфейсу: получают text → возвращают
dataclass/словарь с результатом; предобученных моделей не требуется
— они обучаются либо на встроенных seed-данных, либо на пользовательских.
"""

from email_analyzer.ml.classifier import EmailClassifier, ClassificationResult
from email_analyzer.ml.spam_detector import SpamDetector, SpamResult
from email_analyzer.ml.summarizer import Summarizer
from email_analyzer.ml.entity_extractor import EntityExtractor, ExtractedEntities
from email_analyzer.ml.language_detector import LanguageDetector, LanguageResult
from email_analyzer.ml.sentiment import SentimentAnalyzer, SentimentResult
from email_analyzer.ml.priority import PriorityScorer, PriorityResult
from email_analyzer.ml.semantic_search import SemanticSearch, SearchHit

__all__ = [
    "EmailClassifier",
    "ClassificationResult",
    "SpamDetector",
    "SpamResult",
    "Summarizer",
    "EntityExtractor",
    "ExtractedEntities",
    "LanguageDetector",
    "LanguageResult",
    "SentimentAnalyzer",
    "SentimentResult",
    "PriorityScorer",
    "PriorityResult",
    "SemanticSearch",
    "SearchHit",
]
