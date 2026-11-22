"""Configuración del servicio por entorno, independiente del entrenamiento histórico."""
from dataclasses import dataclass
import os
from pathlib import Path

from src.config import ROOT_DIR

SERVING_DIR = ROOT_DIR / "outputs" / "models" / "serving"


@dataclass(frozen=True)
class Settings:
    model_path: Path = SERVING_DIR / "logistic_regression_drybean.joblib"
    manifest_path: Path = SERVING_DIR / "model_manifest.json"
    max_batch_size: int = 1000
    max_request_bytes: int = 2 * 1024 * 1024
    log_level: str = "INFO"

    def __post_init__(self):
        if self.max_batch_size < 1 or self.max_batch_size > 1000:
            raise ValueError("MAX_BATCH_SIZE debe estar entre 1 y 1000")
        if self.max_request_bytes < 1:
            raise ValueError("MAX_REQUEST_BYTES debe ser positivo")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL no es válido")

    @classmethod
    def from_env(cls):
        defaults = cls()
        return cls(
            model_path=Path(os.getenv("MODEL_PATH", str(defaults.model_path))),
            manifest_path=Path(os.getenv("MODEL_MANIFEST_PATH", str(defaults.manifest_path))),
            max_batch_size=int(os.getenv("MAX_BATCH_SIZE", "1000")),
            max_request_bytes=int(os.getenv("MAX_REQUEST_BYTES", str(defaults.max_request_bytes))),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
