"""Límite de cuerpo y registro HTTP en ASGI, incluyendo transferencias fragmentadas."""
import json
import logging
from time import perf_counter
from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("drybean.api")


class HTTPBoundary:
    def __init__(self, app: ASGIApp, max_request_bytes: int, model_version):
        self.app = app
        self.max_request_bytes = max_request_bytes
        self.model_version = model_version

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = str(uuid4())
        state = scope.setdefault("state", {})
        state["request_id"] = request_id
        started = perf_counter()
        status = 500
        response_started = False

        async def observed_send(message):
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                response_started = True
                message = {
                    **message,
                    "headers": [*message.get("headers", []), (b"x-request-id", request_id.encode())],
                }
            await send(message)

        async def error(code, detail):
            response = JSONResponse({"detail": detail, "request_id": request_id}, status_code=code)
            await response(scope, receive, observed_send)

        try:
            headers = dict(scope["headers"])
            if b"content-length" in headers:
                try:
                    declared_size = int(headers[b"content-length"])
                    if declared_size < 0:
                        raise ValueError
                except ValueError:
                    await error(400, "Content-Length no es válido")
                    return
                if declared_size > self.max_request_bytes:
                    await error(413, "La petición supera el límite de bytes")
                    return

            # Se cuenta cada fragmento antes de que FastAPI decodifique el JSON.
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                if len(body) + len(chunk) > self.max_request_bytes:
                    await error(413, "La petición supera el límite de bytes")
                    return
                body.extend(chunk)
                if not message.get("more_body", False):
                    break
            replayed = False

            async def replay_receive():
                nonlocal replayed
                if not replayed:
                    replayed = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            await self.app(scope, replay_receive, observed_send)
        except Exception as exc:
            logger.error("request_id=%s exception_type=%s", request_id, type(exc).__name__)
            if response_started:
                raise
            await error(500, "No se pudo completar la solicitud")
        finally:
            logger.info(json.dumps({
                "request_id": request_id,
                "method": scope["method"],
                "path": scope["path"],
                "status": status,
                "latency_ms": round((perf_counter() - started) * 1000, 3),
                "batch_size": state.get("batch_size", 0),
                "model_version": self.model_version(),
            }))
