"""Valida CSV antes de la petición y conserva las columnas originales para la descarga."""
import csv
from dataclasses import dataclass
from io import StringIO

import pandas as pd
from pydantic import ValidationError

from deploy.web.api.schemas import BeanFeatures, PredictionResponse
from deploy.web.dashboard.settings import DashboardSettings

ALIASES = {"AspectRation": "AspectRatio", "roundness": "Roundness"}
FEATURES = list(BeanFeatures.model_fields)


class CSVError(ValueError):
    """Archivo que no cumple el formato de inferencia."""


@dataclass
class PreparedBatch:
    original: pd.DataFrame
    instances: list[dict]


def prepare_csv(content: bytes, settings: DashboardSettings, classes: list[str]) -> PreparedBatch:
    if len(content) > settings.max_request_bytes:
        raise CSVError("El archivo supera el límite de 2 MiB o el límite configurado.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CSVError("Guarda el archivo como CSV UTF-8 separado por comas.") from exc
    try:
        rows = csv.reader(StringIO(text), strict=True)
        headers = next(rows, [])
        canonical = [ALIASES.get(name, name) for name in headers]
        if len(set(canonical)) != len(canonical):
            raise CSVError("Hay columnas repetidas o un alias junto a su nombre canónico.")
        missing = set(FEATURES) - set(canonical)
        extra = set(canonical) - set(FEATURES) - {"Class"}
        if missing or extra:
            details = []
            if missing:
                details.append("Faltan: " + ", ".join(sorted(missing)))
            if extra:
                details.append("No reconocidas: " + ", ".join(sorted(extra)))
            raise CSVError(". ".join(details))
        originals, instances = [], []
        errors = []
        for line, values in enumerate(rows, start=2):
            if not values:
                continue
            if len(originals) >= settings.max_batch_size:
                raise CSVError(f"El archivo admite como máximo {settings.max_batch_size} filas; no se dividirá automáticamente.")
            originals.append(values)
            if len(values) != len(headers):
                errors.append(f"Fila {line}: cantidad de columnas incorrecta.")
                continue
            row = dict(zip(canonical, values))
            try:
                instance = BeanFeatures.model_validate({name: float(row[name]) for name in FEATURES})
                if "Class" in row and row["Class"] not in classes:
                    raise ValueError("etiqueta Class desconocida o vacía")
                instances.append(instance.model_dump())
            except ValidationError as exc:
                fields = ", ".join(str(error["loc"][0]) for error in exc.errors())
                errors.append(f"Fila {line}: revisa {fields}; se requieren números finitos dentro de su dominio.")
            except ValueError:
                errors.append(f"Fila {line}: medidas no numéricas o etiqueta Class desconocida.")
        if errors:
            raise CSVError("\n".join(errors[:10]) + ("\nHay más filas inválidas." if len(errors) > 10 else ""))
        if not originals:
            raise CSVError("El archivo no contiene filas para predecir.")
        return PreparedBatch(pd.DataFrame(originals, columns=headers), instances)
    except csv.Error as exc:
        raise CSVError("No se pudo leer el CSV. Revisa comillas y separadores.") from exc


def results_frame(batch: PreparedBatch, response: PredictionResponse) -> pd.DataFrame:
    if len(response.predictions) != len(batch.original):
        raise ValueError("La cantidad de predicciones no coincide con las filas del archivo")
    result = batch.original.copy()
    result["predicted_class"] = [item.predicted_class for item in response.predictions]
    result["confidence"] = [item.confidence for item in response.predictions]
    result["model_version"] = response.model_version
    return result
