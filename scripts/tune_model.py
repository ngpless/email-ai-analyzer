"""Подбор гиперпараметров и лучшей архитектуры классификатора.

Сравниваем несколько кандидатов на holdout 80/20 + 5-fold CV:
    1. LogReg + word + char n-grams (текущий дефолт);
    2. LogReg + только char n-grams;
    3. ComplementNB + word + char n-grams;
    4. LinearSVC (calibrated) + word + char n-grams;
    5. LogReg + word (1..3) + char (2..6) — расширенные диапазоны.

Скрипт печатает сводную таблицу и позволяет выбрать лучший конфиг.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from email_analyzer.ml.classifier import SEED_DATASET, _normalize  # type: ignore


def _word_char(word_range=(1, 2), char_range=(3, 5)) -> FeatureUnion:
    return FeatureUnion([
        ("word", TfidfVectorizer(
            analyzer="word", ngram_range=word_range,
            min_df=1, sublinear_tf=True,
        )),
        ("char", TfidfVectorizer(
            analyzer="char_wb", ngram_range=char_range,
            min_df=1, sublinear_tf=True,
        )),
    ])


def _char_only(char_range=(2, 6)) -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb", ngram_range=char_range,
        min_df=1, sublinear_tf=True,
    )


def candidates() -> dict[str, Pipeline]:
    return {
        "LogReg + word(1-2) + char(3-5)": Pipeline([
            ("features", _word_char()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", C=4.0)),
        ]),
        "LogReg + char(2-6)": Pipeline([
            ("features", _char_only()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", C=4.0)),
        ]),
        "ComplementNB + word+char": Pipeline([
            ("features", _word_char()),
            ("clf", ComplementNB(alpha=0.3)),
        ]),
        "LinearSVC(calibrated) + word+char": Pipeline([
            ("features", _word_char()),
            ("clf", CalibratedClassifierCV(
                LinearSVC(C=1.0, class_weight="balanced", max_iter=5000),
                cv=3,
            )),
        ]),
        "LogReg + word(1-3) + char(2-6)": Pipeline([
            ("features", _word_char(word_range=(1, 3), char_range=(2, 6))),
            ("clf", LogisticRegression(max_iter=3000, class_weight="balanced", C=4.0)),
        ]),
    }


def evaluate(name: str, pipe: Pipeline, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    # Holdout
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )
    pipe.fit(x_tr, y_tr)
    holdout_acc = accuracy_score(y_te, pipe.predict(x_te))

    # 5-fold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_accs: list[float] = []
    for tr_idx, te_idx in skf.split(x, y):
        fresh = pipe  # заново fit — scikit-learn переобучит внутренние состояния
        fresh.fit(x[tr_idx], y[tr_idx])
        fold_accs.append(accuracy_score(y[te_idx], fresh.predict(x[te_idx])))
    cv_acc = float(np.mean(fold_accs))
    return holdout_acc, cv_acc


def main() -> int:
    texts = np.asarray([_normalize(t) for t, _ in SEED_DATASET])
    labels = np.asarray([c.value for _, c in SEED_DATASET])
    print(f"Обучающий корпус: {len(texts)} примеров, классов: {len(set(labels))}")
    print()
    print(f"{'Модель':<45} {'Holdout':>10} {'5-fold':>10}")
    print("-" * 68)
    results = []
    for name, pipe in candidates().items():
        ho, cv = evaluate(name, pipe, texts, labels)
        print(f"{name:<45} {ho:>10.3f} {cv:>10.3f}")
        results.append((name, ho, cv))

    best = max(results, key=lambda r: r[1] + r[2])
    print()
    print(f"Лучшая модель: {best[0]} (holdout={best[1]:.3f}, cv={best[2]:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
