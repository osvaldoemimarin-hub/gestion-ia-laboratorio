"""FastAPI sirve el Pipeline preparado; el ciclo de inicio valida y carga una sola vez."""
from contextlib import asynccontextmanager
import logging
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import pandas as pd
from starlette.exceptions import HTTPException as StarletteHTTPException

from deploy.web.api.middleware import HTTPBoundary
from deploy.web.api.model_store import ModelBundle, load_bundle
from deploy.web.api.schemas import ErrorResponse, ModelInfo, PredictionRequest, PredictionResponse
from deploy.web.api.settings import Settings
from src.predict import predict_probabilities


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(application):
        application.state.bundle = load_bundle(settings)
        try:
            yield
        finally:
            application.state.bundle = None

    application = FastAPI(
        title="Dry Bean — API de clasificación",
        version="1.0.0",
        description="Predice variedades a partir de 16 características geométricas originales.",
        lifespan=lifespan,
    )
    application.state.bundle = None
    application.add_middleware(
        HTTPBoundary,
        max_request_bytes=settings.max_request_bytes,
        model_version=lambda: (
            application.state.bundle.info.model_version if application.state.bundle else "unavailable"
        ),
    )
    logger = logging.getLogger("drybean.api")
    logger.setLevel(settings.log_level)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler(sys.stdout))

    def get_bundle() -> ModelBundle:
        if application.state.bundle is None:
            raise HTTPException(503, "El modelo no está disponible")
        return application.state.bundle

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Se omiten valores de entrada: NaN no es JSON válido y las filas no van al log.
        details = [
            {"loc": list(error["loc"]), "type": error["type"], "msg": error["msg"]}
            for error in exc.errors()
        ]
        return JSONResponse({"detail": details, "request_id": request.state.request_id}, status_code=422)

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            {"detail": exc.detail, "request_id": request.state.request_id},
            status_code=exc.status_code, headers=exc.headers,
        )

    @application.get("/health/live", tags=["Salud"])
    def live():
        return {"status": "alive"}

    @application.get("/health/ready", tags=["Salud"], responses={503: {"model": ErrorResponse}})
    def ready():
        bundle = get_bundle()
        return {"status": "ready", "model_version": bundle.info.model_version}

    @application.get("/api/v1/model", response_model=ModelInfo, tags=["Modelo"])
    def model_info():
        return get_bundle().info

    @application.post(
        "/api/v1/predict", response_model=PredictionResponse, tags=["Inferencia"],
        responses={code: {"model": ErrorResponse} for code in (413, 422, 500, 503)},
    )
    def predict(payload: PredictionRequest, request: Request):
        request.state.batch_size = len(payload.instances)
        if len(payload.instances) > settings.max_batch_size:
            raise HTTPException(422, f"El lote admite como máximo {settings.max_batch_size} filas")
        bundle = get_bundle()
        data = pd.DataFrame(
            [instance.model_dump() for instance in payload.instances], columns=bundle.info.features,
        )
        probabilities = predict_probabilities(bundle.model, data)
        results = []
        for index, row in enumerate(probabilities):
            winner = int(row.argmax())
            results.append({
                "index": index,
                "predicted_class": bundle.info.classes[winner],
                "confidence": float(row[winner]),
                "probabilities": dict(zip(bundle.info.classes, row.tolist())),
            })
        return {
            "request_id": request.state.request_id,
            "model_version": bundle.info.model_version,
            "predictions": results,
        }

    return application


app = create_app()
