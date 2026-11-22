"""Límites de la interfaz y dirección del servicio, configurables por entorno."""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DashboardSettings:
    api_base_url: str = "http://127.0.0.1:8000"
    max_batch_size: int = 1000
    max_request_bytes: int = 2 * 1024 * 1024

    @classmethod
    def from_env(cls):
        settings = cls(
            api_base_url=os.getenv("API_BASE_URL", cls.api_base_url).rstrip("/"),
            max_batch_size=int(os.getenv("MAX_BATCH_SIZE", "1000")),
            max_request_bytes=int(os.getenv("MAX_REQUEST_BYTES", str(cls.max_request_bytes))),
        )
        if not settings.api_base_url.startswith(("http://", "https://")):
            raise ValueError("API_BASE_URL debe ser una dirección HTTP o HTTPS")
        if not 1 <= settings.max_batch_size <= 1000 or settings.max_request_bytes < 1:
            raise ValueError("Los límites de carga no son válidos")
        return settings
