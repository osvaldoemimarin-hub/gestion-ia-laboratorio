"""Carga, calidad y preparación de datos (CRISP-DM fases 2 y 3)."""
from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

from src import config

COLUMN_FIXES = {"AspectRation": "AspectRatio", "roundness": "Roundness"}


def load_data(prefer_uci: bool = True, save_raw: bool = True) -> pd.DataFrame:
    """Carga el Dry Bean Dataset.

    Intenta primero la fuente oficial (UCI, id=602) con ``ucimlrepo``. Si no hay
    conexión, usa la copia local ``data/raw/Dry_Bean_Dataset.xlsx`` para que el
    proyecto siga siendo reproducible sin internet.
    """
    df = None
    if prefer_uci:
        try:
            from ucimlrepo import fetch_ucirepo

            dry_bean = fetch_ucirepo(id=config.UCI_DATASET_ID)
            df = pd.concat([dry_bean.data.features, dry_bean.data.targets], axis=1)
            df.attrs["source"] = "UCI ML Repository (ucimlrepo, id=602)"
        except Exception as exc:  # sin red, API caída, etc.
            print(f"[load_data] No se pudo descargar desde UCI ({exc}). Uso copia local.")
    if df is None:
        # El .xlsx original trae dos nombres distintos a la versión de UCI;
        # se normalizan para que el modelo guardado funcione con ambas fuentes.
        df = pd.read_excel(config.RAW_XLSX).rename(columns=COLUMN_FIXES)
        df.attrs["source"] = f"Copia local {config.RAW_XLSX.name}"

    if save_raw:
        config.ensure_dirs()
        df.to_csv(config.RAW_CSV, index=False)
    return df


def quality_report(df: pd.DataFrame) -> dict:
    """Resumen de calidad: nulos, duplicados, tipos y distribución de clases."""
    return {
        "filas": int(df.shape[0]),
        "columnas": int(df.shape[1]),
        "nulos_totales": int(df.isna().sum().sum()),
        "nulos_por_columna": df.isna().sum().to_dict(),
        "duplicados": int(df.duplicated().sum()),
        "columnas_no_numericas": [
            c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])
        ],
        "clases": df[config.TARGET].value_counts().to_dict(),
    }


def clean_data(df: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    """Limpieza básica: elimina filas duplicadas completas."""
    clean = df.drop_duplicates().reset_index(drop=True)
    if save:
        config.ensure_dirs()
        clean.to_csv(config.PROCESSED_CSV, index=False)
    return clean


def split_data(df: pd.DataFrame):
    """Separa X/y y hace train/test estratificado (80/20, semilla 42)."""
    X = df.drop(columns=config.TARGET)
    y = df[config.TARGET]
    return train_test_split(
        X,
        y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=y,
    )
