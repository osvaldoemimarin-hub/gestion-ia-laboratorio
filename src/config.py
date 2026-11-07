"""Configuración central del proyecto (TDSP: una sola fuente de verdad para rutas y semillas)."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODELS_DIR = ROOT_DIR / "outputs" / "models"
REPORTS_DIR = ROOT_DIR / "outputs" / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

RAW_XLSX = DATA_RAW_DIR / "Dry_Bean_Dataset.xlsx"
RAW_CSV = DATA_RAW_DIR / "dry_bean_raw.csv"
PROCESSED_CSV = DATA_PROCESSED_DIR / "dry_bean_clean.csv"

MODEL_PATH = MODELS_DIR / "random_forest_drybean.joblib"
BASELINE_PATH = MODELS_DIR / "logistic_regression_drybean.joblib"

UCI_DATASET_ID = 602
TARGET = "Class"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def ensure_dirs() -> None:
    """Crea las carpetas de salida si no existen."""
    for folder in (DATA_RAW_DIR, DATA_PROCESSED_DIR, MODELS_DIR, REPORTS_DIR, FIGURES_DIR):
        folder.mkdir(parents=True, exist_ok=True)
