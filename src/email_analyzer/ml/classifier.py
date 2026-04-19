"""Классификатор писем по категориям.

Использует sklearn: TF-IDF + логистическая регрессия. Маленькая и быстрая
модель, пригодная для offline-работы на ноутбуке. Обучается либо на
seed-наборе (встроен ниже), либо на пользовательских данных.

Интерфейс специально сделан простым, чтобы легко заменить на BERT/LLM
без изменения кода потребителей.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from email_analyzer.db.models import Category


SEED_DATASET: List[Tuple[str, Category]] = [
    ("Совещание перенесено на понедельник, 10:00.", Category.WORK),
    ("Прошу согласовать договор с контрагентом до среды.", Category.WORK),
    ("Отчёт по проекту готов, ссылка на Google Docs внутри.", Category.WORK),
    ("Напоминание: завтра ежемесячный обзор команды.", Category.WORK),
    ("Просьба подписать документ во вложении.", Category.WORK),

    ("Поздравляю с днём рождения! Желаю всего самого лучшего.", Category.PERSONAL),
    ("Мам, привет. Как дела? Напиши, как будет минутка.", Category.PERSONAL),
    ("Собираемся в субботу на даче, присоединяйся!", Category.PERSONAL),
    ("Фото с отпуска прикрепил, смотри :)", Category.PERSONAL),

    ("Скидка 50% только сегодня! Успей купить.", Category.PROMO),
    ("Новая коллекция уже в продаже. Бесплатная доставка.", Category.PROMO),
    ("Промокод SALE20 на любой заказ.", Category.PROMO),
    ("Подпишись на рассылку и получай эксклюзивные акции.", Category.PROMO),

    ("СРОЧНО! Вы выиграли миллион, перейдите по ссылке прямо сейчас!!!", Category.SPAM),
    ("Получите кредит без проверки, 0%, оформление онлайн.", Category.SPAM),
    ("Viagra очень дёшево, закажи сейчас, доставка бесплатная.", Category.SPAM),

    ("Ваш банк заблокировал карту. Срочно введите данные по ссылке.", Category.PHISHING),
    ("Подтвердите пароль Google, иначе аккаунт будет удалён.", Category.PHISHING),
    ("Верификация карты требует ввода CVV по ссылке ниже.", Category.PHISHING),

    ("Кандидат прошёл итоговое собеседование, ждём решения.", Category.IMPORTANT),
    ("ВНИМАНИЕ: на сервере обнаружена критическая уязвимость.", Category.IMPORTANT),
    ("Срок сдачи отчёта — завтра до 18:00, напоминаю.", Category.IMPORTANT),
]


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    category: Category
    confidence: float
    top_scores: Tuple[Tuple[Category, float], ...]


def _normalize(text: str) -> str:
    """Привести текст к нижнему регистру и убрать мусор."""
    text = text.lower()
    text = re.sub(r"https?://\S+", " url ", text)
    text = re.sub(r"\S+@\S+", " email ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class EmailClassifier:
    """Классификатор писем."""

    def __init__(self, model_path: Optional[Path] = None) -> None:
        self.model_path = model_path
        self._pipeline: Optional[Pipeline] = None
        self._categories: List[Category] = []

    # ---------- Обучение ----------

    def fit(
        self,
        texts: Sequence[str],
        labels: Sequence[Category],
    ) -> None:
        if len(texts) != len(labels):
            raise ValueError("len(texts) != len(labels)")
        if len(set(labels)) < 2:
            raise ValueError("need ≥ 2 distinct categories to train")

        normalized = [_normalize(t) for t in texts]
        self._pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("clf", LogisticRegression(max_iter=500, class_weight="balanced")),
            ]
        )
        self._pipeline.fit(normalized, [c.value for c in labels])
        self._categories = sorted(
            {Category(c) for c in self._pipeline.classes_},
            key=lambda c: c.value,
        )

    def fit_seed(self) -> None:
        """Обучить модель на встроенном seed-наборе."""
        texts = [t for t, _ in SEED_DATASET]
        labels = [c for _, c in SEED_DATASET]
        self.fit(texts, labels)

    # ---------- Сохранение ----------

    def save(self, path: Optional[Path] = None) -> Path:
        target = path or self.model_path
        if target is None:
            raise ValueError("model path not specified")
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._pipeline, target)
        return target

    def load(self, path: Optional[Path] = None) -> None:
        source = path or self.model_path
        if source is None or not source.exists():
            raise FileNotFoundError(f"model file not found: {source}")
        self._pipeline = joblib.load(source)
        self._categories = sorted(
            {Category(c) for c in self._pipeline.classes_},
            key=lambda c: c.value,
        )

    # ---------- Инференс ----------

    def is_fitted(self) -> bool:
        return self._pipeline is not None

    def predict(self, text: str) -> ClassificationResult:
        if not self.is_fitted():
            raise RuntimeError("classifier is not fitted, call fit()/fit_seed() first")
        assert self._pipeline is not None

        normalized = _normalize(text)
        proba = self._pipeline.predict_proba([normalized])[0]
        classes = [Category(c) for c in self._pipeline.classes_]

        pairs = sorted(
            zip(classes, proba, strict=True),
            key=lambda p: p[1],
            reverse=True,
        )
        best_category, best_confidence = pairs[0]
        return ClassificationResult(
            category=best_category,
            confidence=float(best_confidence),
            top_scores=tuple((c, float(p)) for c, p in pairs),
        )
