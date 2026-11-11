"""Verifica el artefacto confiable y su entorno antes de permitir inferencia HTTP."""
from dataclasses import dataclass
import hashlib
from importlib.metadata import version
import json
import platform
import warnings

from sklearn.exceptions import InconsistentVersionWarning

from deploy.web.api.schemas import BeanFeatures, ModelInfo
from deploy.web.api.settings import Settings
from src.predict import load_model

RUNTIME_PACKAGES = {"numpy", "pandas", "scipy", "scikit-learn", "joblib"}


@dataclass(frozen=True)
class ModelBundle:
    model: object
    info: ModelInfo


def load_bundle(settings: Settings) -> ModelBundle:
    """Falla antes de servir si cambian bytes, dependencias, variables o clases.

    La huella detecta cambios accidentales; el manifiesto debe proceder de una
    entrega confiable porque joblib no es un formato para archivos del usuario.
    """
    manifest = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    if manifest["manifest_version"] != 1:
        raise ValueError("Versión de manifiesto no soportada")
    digest = hashlib.sha256(settings.model_path.read_bytes()).hexdigest()
    if digest != manifest["model_sha256"]:
        raise ValueError("La huella del modelo no coincide con el manifiesto")
    if platform.python_version_tuple()[:2] != tuple(manifest["python_version"].split(".")[:2]):
        raise ValueError("El modelo requiere la misma versión mayor y menor de Python")
    if set(manifest["packages"]) != RUNTIME_PACKAGES:
        raise ValueError("El manifiesto no registra las dependencias de inferencia esperadas")
    for name, expected in manifest["packages"].items():
        if version(name) != expected:
            raise ValueError(f"Versión incompatible de {name}: se requiere {expected}")
    info = ModelInfo.model_validate(manifest)
    features = info.features
    if len(features) != len(set(features)) or set(features) != set(BeanFeatures.model_fields):
        raise ValueError("Las variables del manifiesto no coinciden con el contrato HTTP")
    with warnings.catch_warnings():
        warnings.simplefilter("error", InconsistentVersionWarning)
        model = load_model(settings.model_path)
    if list(model.feature_names_in_) != features or list(model.classes_) != info.classes:
        raise ValueError("El esquema del artefacto no coincide con el manifiesto")
    return ModelBundle(model=model, info=info)
