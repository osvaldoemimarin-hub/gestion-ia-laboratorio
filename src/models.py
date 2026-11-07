"""Definición de modelos (CRISP-DM fase 4: modelado)."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_STATE


def build_baseline() -> Pipeline:
    """Baseline: estandarización + regresión logística multiclase."""
    return Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
    ])


def build_forest(n_estimators: int = 200, **kwargs) -> RandomForestClassifier:
    """Modelo mejorado: Random Forest con pesos balanceados por clase."""
    params = dict(
        n_estimators=n_estimators,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        n_jobs=-1,
    )
    params.update(kwargs)
    return RandomForestClassifier(**params)
