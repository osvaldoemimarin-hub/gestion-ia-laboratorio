"""Medidas del formulario y muestra compartida por las vistas individual y CSV."""
import json
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
EXAMPLE = json.loads((ASSETS_DIR / "example_request.json").read_text(encoding="utf-8"))["instances"][0]

LABELS = {
    "Area": "Área", "Perimeter": "Perímetro", "MajorAxisLength": "Eje mayor",
    "MinorAxisLength": "Eje menor", "AspectRatio": "Relación de aspecto",
    "Eccentricity": "Excentricidad", "ConvexArea": "Área convexa", "EquivDiameter": "Diámetro equivalente",
    "Extent": "Extensión", "Solidity": "Solidez", "Roundness": "Redondez", "Compactness": "Compacidad",
    "ShapeFactor1": "Factor de forma 1", "ShapeFactor2": "Factor de forma 2",
    "ShapeFactor3": "Factor de forma 3", "ShapeFactor4": "Factor de forma 4",
}
SIZE_FIELDS = {"Area", "Perimeter", "MajorAxisLength", "MinorAxisLength", "ConvexArea", "EquivDiameter"}
