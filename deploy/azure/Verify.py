"""Comprueba HTTPS y una predicción real usando el protocolo WebSocket de Streamlit.

Requiere el entorno dev fijado y acceso al dashboard. No abre la API
al exterior ni simula respuestas: el formulario remoto debe ejecutar inferencia.
"""
import argparse
import json
from pathlib import Path
from time import monotonic
from urllib.request import urlopen

from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.Alert_pb2 import Alert
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from websockets.sync.client import connect


def read_render(socket):
    elements = []
    page_hash = ""
    for _ in range(250):
        message = ForwardMsg()
        message.ParseFromString(socket.recv(timeout=45))
        kind = message.WhichOneof("type")
        if kind == "new_session":
            page_hash = message.new_session.page_script_hash
        elif kind == "delta" and message.delta.HasField("new_element"):
            element = message.delta.new_element
            if element.HasField("exception"):
                raise RuntimeError("El dashboard remoto produjo una excepción al renderizar")
            if element.HasField("alert") and element.alert.format == Alert.ERROR:
                raise RuntimeError(f"El dashboard remoto informó un error: {element.alert.body}")
            elements.append(element)
        elif kind == "script_finished":
            return elements, page_hash
    raise RuntimeError("El dashboard no terminó de renderizar dentro del límite de mensajes")


def verify(url: str) -> dict:
    url = url.rstrip("/")
    if not url.startswith("https://"):
        raise ValueError("La verificación de Azure requiere una URL HTTPS")
    with urlopen(url + "/_stcore/health", timeout=20) as response:
        if response.status != 200:
            raise RuntimeError("La sonda HTTPS no responde correctamente")
    with connect(
        url.replace("https://", "wss://", 1) + "/_stcore/stream",
        origin=url, subprotocols=["streamlit"], open_timeout=20,
    ) as socket:
        initial = BackMsg()
        initial.rerun_script.query_string = ""
        socket.send(initial.SerializeToString())
        elements, page_hash = read_render(socket)
        inputs = [element.number_input for element in elements if element.HasField("number_input")]
        buttons = [element.button for element in elements if element.HasField("button")]
        submit = next((button for button in buttons if button.label == "Clasificar grano"), None)
        if len(inputs) != 16 or submit is None:
            raise RuntimeError("El formulario remoto no está disponible o el modelo no respondió")
        request = BackMsg()
        request.rerun_script.page_script_hash = page_hash
        for widget in inputs:
            state = request.rerun_script.widget_states.widgets.add()
            state.id = widget.id
            state.double_value = widget.default
        trigger = request.rerun_script.widget_states.widgets.add()
        trigger.id = submit.id
        trigger.trigger_value = True
        started = monotonic()
        socket.send(request.SerializeToString())
        results, _ = read_render(socket)
        elapsed = round((monotonic() - started) * 1000, 2)
        metrics = {element.metric.label: element.metric.body for element in results if element.HasField("metric")}
        if metrics.get("Variedad predicha") != "SEKER":
            raise RuntimeError("La inferencia del ejemplo no devolvió SEKER")
        return {
            "dashboard_url": url,
            "https_health": 200,
            "websocket": "ok",
            "prediction": metrics["Variedad predicha"],
            "displayed_probability": metrics.get("Probabilidad del modelo"),
            "form_roundtrip_ms": elapsed,
            "note": "Prueba funcional de una fila; no es una medición de capacidad ni p95",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verifica el dashboard remoto y su API interna")
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    report = json.dumps(verify(arguments.url), ensure_ascii=False, indent=2)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(report + "\n", encoding="utf-8")
    print(report)
