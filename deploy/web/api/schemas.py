"""Contrato v1: medidas originales finitas, sin etiquetas ni conversiones de texto."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

PositiveMeasure = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]
UnitRatio = Annotated[float, Field(strict=True, gt=0, le=1, allow_inf_nan=False)]
EccentricityValue = Annotated[float, Field(strict=True, ge=0, lt=1, allow_inf_nan=False)]


class BeanFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Area: PositiveMeasure
    Perimeter: PositiveMeasure
    MajorAxisLength: PositiveMeasure
    MinorAxisLength: PositiveMeasure
    AspectRatio: PositiveMeasure
    Eccentricity: EccentricityValue
    ConvexArea: PositiveMeasure
    EquivDiameter: PositiveMeasure
    Extent: UnitRatio
    Solidity: UnitRatio
    Roundness: UnitRatio
    Compactness: UnitRatio
    ShapeFactor1: PositiveMeasure
    ShapeFactor2: PositiveMeasure
    ShapeFactor3: PositiveMeasure
    ShapeFactor4: PositiveMeasure


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instances: list[BeanFeatures] = Field(min_length=1, max_length=1000)


class Prediction(BaseModel):
    index: int
    predicted_class: str
    confidence: float
    probabilities: dict[str, float]


class PredictionResponse(BaseModel):
    request_id: str
    model_version: str
    predictions: list[Prediction]


class ErrorResponse(BaseModel):
    detail: str | list[dict]
    request_id: str


class ModelInfo(BaseModel):
    model_version: str
    algorithm: str
    model_sha256: str
    features: list[str]
    classes: list[str]
    metrics: dict[str, float]
    evaluation: dict
