"""Pruebas mínimas de la Definition of Done (usan la copia local, sin internet)."""
import pandas as pd
import pytest

from src import config
from src.data import clean_data, load_data, quality_report, split_data
from src.models import build_baseline
from src.predict import load_model, predict_bean_class


@pytest.fixture(scope="module")
def df():
    return load_data(prefer_uci=False, save_raw=False)


def test_dataset_shape(df):
    assert df.shape == (13611, 17)
    assert df[config.TARGET].nunique() == 7


def test_quality_report(df):
    q = quality_report(df)
    assert q["nulos_totales"] == 0
    assert q["duplicados"] == 68
    assert q["columnas_no_numericas"] == [config.TARGET]


def test_clean_and_split(df):
    clean = clean_data(df, save=False)
    assert clean.duplicated().sum() == 0
    X_train, X_test, y_train, y_test = split_data(clean)
    assert len(X_test) == pytest.approx(0.2 * len(clean), abs=1)
    # estratificación: proporciones casi iguales
    diff = (y_train.value_counts(normalize=True) - y_test.value_counts(normalize=True)).abs()
    assert diff.max() < 0.005


def test_baseline_beats_chance(df):
    X_train, X_test, y_train, y_test = split_data(clean_data(df, save=False))
    acc = (build_baseline().fit(X_train, y_train).predict(X_test) == y_test).mean()
    assert acc > 0.85


@pytest.mark.skipif(not config.MODEL_PATH.exists(), reason="Ejecuta primero el pipeline")
def test_saved_model_predicts(df):
    model = load_model()
    sample = df.drop(columns=config.TARGET).iloc[[0]]
    assert predict_bean_class(model, sample) in set(df[config.TARGET])
