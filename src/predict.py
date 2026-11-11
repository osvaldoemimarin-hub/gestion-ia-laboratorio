"""Mini despliegue local (CRISP-DM fase 6).

Uso como módulo:
    from src.predict import load_model, predict_bean_class

Uso por consola (predice las primeras N filas de un CSV con las 16 variables):
    python -m src.predict --input data/processed/dry_bean_clean.csv --n 5
"""
from __future__ import annotations

import argparse

import joblib
import pandas as pd

from src import config


def load_model(path=config.MODEL_PATH):
    return joblib.load(path)


def predict_bean_class(model, input_data: pd.DataFrame):
    """Devuelve la clase predicha para la primera fila de ``input_data``."""
    prediction = model.predict(input_data)
    return prediction[0]


def predict_batch(model, input_data: pd.DataFrame) -> pd.DataFrame:
    """Predicciones con probabilidad de la clase ganadora."""
    proba = predict_probabilities(model, input_data)
    out = input_data.copy()
    out["predicted_class"] = model.classes_[proba.argmax(axis=1)]
    out["confidence"] = proba.max(axis=1).round(4)
    return out


def predict_probabilities(model, input_data: pd.DataFrame):
    """Conserva precisión y orden de clases para consumidores HTTP y CLI."""
    return model.predict_proba(input_data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Predice la variedad de frijol seco.")
    parser.add_argument("--input", required=True, help="CSV con las 16 variables geométricas")
    parser.add_argument("--n", type=int, default=5, help="Número de filas a predecir")
    args = parser.parse_args()

    model = load_model()
    data = pd.read_csv(args.input).head(args.n)
    real = data.pop(config.TARGET) if config.TARGET in data.columns else None
    result = predict_batch(model, data)
    if real is not None:
        result.insert(0, "real_class", real.values)
    print(result[[c for c in ("real_class", "predicted_class", "confidence") if c in result]])


if __name__ == "__main__":
    main()
