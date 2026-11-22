"""Entrena y evalúa el artefacto HTTP sin sobrescribir la evidencia histórica.

Ejecutar explícitamente con el entorno dev fijado; la API nunca importa este módulo.
"""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess

import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from src import config
from src.data import clean_data, load_data, split_data
from src.models import build_baseline

RUNTIME_PACKAGES = ("numpy", "pandas", "scipy", "scikit-learn", "joblib")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output_dir: Path) -> dict:
    """Escribe modelo, evaluación y ejemplo de petición usando únicamente el Excel local."""
    df = clean_data(load_data(prefer_uci=False, save_raw=False), save=False)
    X_train, X_test, y_train, y_test = split_data(df)
    model = build_baseline().fit(X_train, y_train)
    predictions = model.predict(X_test)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "logistic_regression_drybean.joblib"
    joblib.dump(model, model_path)
    sources = ("src/config.py", "src/data.py", "src/models.py", "deploy/web/prepare_serving_model.py")
    # Git cambia CRLF/LF según el host; la procedencia del código usa texto canónico.
    source_hashes = {
        name: hashlib.sha256((config.ROOT_DIR / name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        for name in sources
    }
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=config.ROOT_DIR,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", *sources], cwd=config.ROOT_DIR,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    digest = sha256_file(model_path)
    manifest = {
        "manifest_version": 1,
        "model_version": f"drybean-lr-{digest[:12]}",
        "algorithm": "StandardScaler + LogisticRegression",
        "model_sha256": digest,
        "features": list(model.feature_names_in_),
        "classes": list(model.classes_),
        "python_version": platform.python_version(),
        "packages": {name: version(name) for name in RUNTIME_PACKAGES},
        "training": {
            "git_commit": commit,
            "source_dirty": bool(dirty),
            "source_sha256": source_hashes,
            "source_hash_normalization": "UTF-8, LF",
            "dataset": "data/raw/Dry_Bean_Dataset.xlsx",
            "dataset_sha256": sha256_file(config.RAW_XLSX),
            "random_state": config.RANDOM_STATE,
            "test_size": config.TEST_SIZE,
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "recipe": "python -m deploy.web.prepare_serving_model",
        },
        "metrics": {
            "accuracy": accuracy_score(y_test, predictions),
            "f1_macro": f1_score(y_test, predictions, average="macro"),
        },
        "evaluation": {
            "source": "holdout local; deduplicado; partición estratificada 80/20",
            "rows": len(X_test),
            "random_state": config.RANDOM_STATE,
            "classification_report": classification_report(y_test, predictions, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, predictions, labels=model.classes_).tolist(),
        },
    }
    (output_dir / "model_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    (output_dir / "example_request.json").write_text(
        json.dumps({"instances": X_test.iloc[:1].to_dict(orient="records")}, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepara el modelo del servicio con el Excel local")
    parser.add_argument("--output-dir", type=Path, default=config.MODELS_DIR / "serving")
    result = prepare(parser.parse_args().output_dir)
    print(json.dumps({"model_version": result["model_version"], "metrics": result["metrics"]}, indent=2))
