"""Evaluación de modelos (CRISP-DM fase 5)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
)


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
    }


def report_df(y_true, y_pred) -> pd.DataFrame:
    """classification_report como DataFrame (precision, recall, f1 por clase)."""
    return pd.DataFrame(classification_report(y_true, y_pred, output_dict=True)).T


def save_confusion_matrix(y_true, y_pred, title: str, path) -> None:
    fig, ax = plt.subplots(figsize=(8, 7))
    ConfusionMatrixDisplay.from_predictions(
        y_true, y_pred, xticks_rotation=45, ax=ax, cmap="Blues", colorbar=False
    )
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def top_confusions(y_true, y_pred, n: int = 5) -> pd.DataFrame:
    """Pares (real, predicho) más frecuentes entre los errores."""
    errors = pd.DataFrame({"real": list(y_true), "predicho": list(y_pred)})
    errors = errors[errors["real"] != errors["predicho"]]
    return (
        errors.value_counts()
        .rename("errores")
        .reset_index()
        .head(n)
    )
