"""Генерация изображений математических формул для главы
«Математическое описание модели».

Формулы отрисовываются через matplotlib.mathtext (подмножество LaTeX,
не требует инсталляции внешнего LaTeX). На выходе — PNG с белым фоном.

Автор: Нефедов А. Г.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "report_assets"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.size"] = 14


def _render(formulas: list[str], name: str,
            line_height: float = 0.9, width: float = 9.5) -> None:
    """Нарисовать список строк-формул друг под другом."""
    height = max(1.0, line_height * len(formulas) + 0.4)
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    for i, fml in enumerate(formulas):
        y = 1.0 - (i + 0.5) / len(formulas)
        ax.text(0.5, y, fml, ha="center", va="center", fontsize=16)
    path = OUT / name
    fig.savefig(path, dpi=170, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  -> {path.relative_to(ROOT)}")


def formula_tfidf() -> None:
    """TF-IDF: term frequency, inverse document frequency, норма."""
    formulas = [
        r"$\mathrm{tf}(t,\,d) = \dfrac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$",
        r"$\mathrm{idf}(t,\,D) = \log\dfrac{N}{1 + |\{d \in D : t \in d\}|}$",
        r"$w_{t,d} = \mathrm{tf}(t,\,d) \cdot \mathrm{idf}(t,\,D)$",
        r"$\hat{\mathbf{w}}_d = \mathbf{w}_d / \|\mathbf{w}_d\|_2$",
    ]
    _render(formulas, "formula_tfidf.png", line_height=1.0)


def formula_logreg() -> None:
    """Multinomial Logistic Regression: softmax + cross-entropy + L2."""
    formulas = [
        r"$z_k(\mathbf{x}) = \mathbf{w}_k^{\top}\,\mathbf{x} + b_k$",
        r"$P(y=k \mid \mathbf{x}) = \dfrac{\exp(z_k)}{\sum_{j=1}^{K} \exp(z_j)}$",
        r"$\mathcal{L}(\theta) = -\dfrac{1}{n} \sum_{i=1}^{n} \sum_{k=1}^{K} \mathbb{1}[y_i = k]\,\log P(y_i = k \mid \mathbf{x}_i)$",
        r"$J(\theta) = \mathcal{L}(\theta) + \dfrac{1}{2 C}\,\sum_{k=1}^{K} \|\mathbf{w}_k\|_2^{2}$",
    ]
    _render(formulas, "formula_logreg.png", line_height=1.05)


def formula_features() -> None:
    """Объединённое признаковое пространство word(1-3) + char(2-6)."""
    formulas = [
        r"$\Phi(d) = \Phi_{\mathrm{word}}(d) \,\oplus\, \Phi_{\mathrm{char}}(d)$",
        r"$\dim\Phi_{\mathrm{word}}(d) = |V_{\mathrm{word}}|, \quad "
        r"n\text{-}\mathrm{grams}\ \in\ \{1,\,2,\,3\}$",
        r"$\dim\Phi_{\mathrm{char}}(d) = |V_{\mathrm{char}}|, \quad "
        r"n\text{-}\mathrm{grams}\ \in\ \{2,\,3,\,4,\,5,\,6\}$",
    ]
    _render(formulas, "formula_features.png", line_height=0.95)


def formula_class_weight() -> None:
    """Balanced class weights для компенсации дисбаланса категорий."""
    formulas = [
        r"$\omega_k = \dfrac{n}{K \cdot n_k}$",
        r"$\mathcal{L}_{\mathrm{balanced}}(\theta) = -\dfrac{1}{n}\sum_{i=1}^{n}"
        r"\,\omega_{y_i}\,\log P(y_i \mid \mathbf{x}_i)$",
    ]
    _render(formulas, "formula_class_weight.png",
            line_height=1.1, width=8.5)


def formula_topk() -> None:
    """Метрика Top-k Accuracy — используется в отчёте (Top-2 = 0.797)."""
    formulas = [
        r"$\mathrm{Top\text{-}k\ Acc} = \dfrac{1}{n}\sum_{i=1}^{n} "
        r"\mathbb{1}\!\left[\,y_i \in \mathrm{top}_k\{P(\cdot\mid\mathbf{x}_i)\}\right]$",
    ]
    _render(formulas, "formula_topk.png", line_height=1.2, width=8.5)


def main() -> int:
    print("Генерация формул…")
    formula_tfidf()
    formula_features()
    formula_class_weight()
    formula_logreg()
    formula_topk()
    print("Готово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
