"""Cliente del dashboard con límites y errores legibles, sin trazas del servidor."""
import json

import httpx
from pydantic import ValidationError

from deploy.web.api.schemas import ModelInfo, PredictionResponse
from deploy.web.dashboard.settings import DashboardSettings


class APIError(Exception):
    """Falla de comunicación o contrato que puede mostrarse al operario."""


class APIClient:
    def __init__(self, settings: DashboardSettings, transport=None):
        self.settings = settings
        self.transport = transport

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            with httpx.Client(
                base_url=self.settings.api_base_url, transport=self.transport,
                timeout=httpx.Timeout(30, connect=5),
            ) as client:
                response = client.request(method, path, **kwargs)
            if response.status_code >= 400:
                messages = {
                    413: "La solicitud supera el tamaño permitido por el servicio.",
                    422: "El servicio rechazó los datos. Revisa las variables y el tamaño del lote.",
                    503: "El modelo todavía no está disponible. Intenta nuevamente en unos segundos.",
                }
                message = messages.get(response.status_code, "El servicio no pudo completar la solicitud.")
                request_id = response.headers.get("x-request-id", "")
                if request_id:
                    message += f" Referencia: {request_id}."
                raise APIError(message)
            return response.json()
        except httpx.TimeoutException as exc:
            raise APIError("El servicio tardó demasiado en responder. Intenta nuevamente.") from exc
        except httpx.RequestError as exc:
            raise APIError("No hay conexión con el servicio de predicción. Intenta nuevamente.") from exc
        except (ValueError, UnicodeError) as exc:
            raise APIError("El servicio devolvió una respuesta que no se puede interpretar.") from exc

    def get_model(self) -> ModelInfo:
        try:
            return ModelInfo.model_validate(self._request("GET", "/api/v1/model"))
        except ValidationError as exc:
            raise APIError("La información del modelo no cumple el contrato esperado.") from exc

    def predict(self, instances: list[dict]) -> PredictionResponse:
        if not 1 <= len(instances) <= self.settings.max_batch_size:
            raise APIError(f"Envía entre 1 y {self.settings.max_batch_size} filas.")
        try:
            body = json.dumps({"instances": instances}, allow_nan=False).encode("utf-8")
        except (ValueError, TypeError) as exc:
            raise APIError("Los datos deben contener únicamente medidas numéricas finitas.") from exc
        if len(body) > self.settings.max_request_bytes:
            raise APIError("Los datos convertidos a JSON superan el tamaño permitido.")
        try:
            result = PredictionResponse.model_validate(self._request(
                "POST", "/api/v1/predict", content=body, headers={"Content-Type": "application/json"},
            ))
        except ValidationError as exc:
            raise APIError("Las predicciones no cumplen el contrato esperado.") from exc
        if [item.index for item in result.predictions] != list(range(len(instances))):
            raise APIError("El servicio devolvió resultados incompletos o fuera de orden.")
        return result
