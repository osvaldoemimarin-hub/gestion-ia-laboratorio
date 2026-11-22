"""Verifica el contrato HTTP contra el artefacto real y fallas de operación."""
import asyncio
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import warnings

from fastapi.testclient import TestClient
import numpy as np
import pytest
from sklearn.exceptions import InconsistentVersionWarning

from deploy.web.api.main import create_app
from deploy.web.api.model_store import load_bundle
from deploy.web.api.schemas import BeanFeatures
from deploy.web.api.settings import Settings
from src.data import clean_data, load_data, split_data


@pytest.fixture(scope="module")
def settings():
    return Settings()


@pytest.fixture(scope="module")
def bundle(settings):
    with warnings.catch_warnings():
        warnings.simplefilter("error", InconsistentVersionWarning)
        return load_bundle(settings)


@pytest.fixture(scope="module")
def data():
    return clean_data(load_data(prefer_uci=False, save_raw=False), save=False)


@pytest.fixture(scope="module")
def instances(data):
    _, X_test, _, _ = split_data(data)
    return X_test.iloc[:10].to_dict(orient="records")


@pytest.fixture(scope="module")
def client(settings):
    with TestClient(create_app(settings)) as http:
        yield http


def test_model_health_and_openapi(client, bundle):
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").json()["model_version"] == bundle.info.model_version
    metadata = client.get("/api/v1/model").json()
    assert metadata["features"] == bundle.info.features
    assert metadata["metrics"]["f1_macro"] > 0.90
    assert metadata["evaluation"]["rows"] == 2709
    assert "/api/v1/predict" in client.get("/openapi.json").json()["paths"]
    assert client.get("/docs").status_code == 200


def test_http_matches_direct_predictions_with_reordered_keys(client, bundle, data):
    _, X_test, _, _ = split_data(data)
    expected_classes = bundle.model.predict(X_test)
    expected_probabilities = bundle.model.predict_proba(X_test)
    # Se recorre todo el holdout en lotes permitidos, invirtiendo las claves JSON.
    results = []
    for start in range(0, len(X_test), 1000):
        records = X_test.iloc[start:start + 1000].to_dict(orient="records")
        response = client.post("/api/v1/predict", json={
            "instances": [dict(reversed(list(row.items()))) for row in records],
        })
        assert response.status_code == 200
        body = response.json()
        assert body["request_id"] == response.headers["x-request-id"]
        assert body["model_version"] == bundle.info.model_version
        assert [row["index"] for row in body["predictions"]] == list(range(len(records)))
        results.extend(body["predictions"])
    assert [row["predicted_class"] for row in results] == expected_classes.tolist()
    probabilities = [[row["probabilities"][name] for name in bundle.info.classes] for row in results]
    np.testing.assert_allclose(probabilities, expected_probabilities, atol=1e-12, rtol=1e-12)
    np.testing.assert_allclose([row["confidence"] for row in results], expected_probabilities.max(axis=1))
    np.testing.assert_allclose(np.sum(probabilities, axis=1), 1)


def test_all_dataset_rows_satisfy_domain_schema(data):
    for row in data.drop(columns="Class").to_dict(orient="records"):
        BeanFeatures.model_validate(row)


@pytest.mark.parametrize("value", [None, True, "123", -1, 0, float("nan"), float("inf"), -float("inf")])
def test_rejects_invalid_measurements(client, instances, value):
    row = {**instances[0], "Area": value}
    response = client.post(
        "/api/v1/predict", content=json.dumps({"instances": [row]}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["request_id"] == response.headers["x-request-id"]
    assert "input" not in response.json()["detail"][0]


@pytest.mark.parametrize("field,value", [
    ("Eccentricity", 1), ("Eccentricity", -0.1), ("Solidity", 1.01),
    ("Roundness", 0), ("Extent", 2), ("Compactness", 1.01),
])
def test_rejects_invalid_ratios(client, instances, field, value):
    response = client.post("/api/v1/predict", json={"instances": [{**instances[0], field: value}]})
    assert response.status_code == 422


@pytest.mark.parametrize("change", ["missing", "extra", "label", "alias"])
def test_requires_exact_canonical_columns(client, instances, change):
    row = instances[0].copy()
    if change == "missing":
        row.pop("Area")
    elif change == "extra":
        row["unexpected"] = 1
    elif change == "label":
        row["Class"] = "SEKER"
    else:
        row["AspectRation"] = row.pop("AspectRatio")
    assert client.post("/api/v1/predict", json={"instances": [row]}).status_code == 422


@pytest.mark.parametrize("payload", [{}, {"instances": []}, {"instances": [1]}, {"instances": [], "other": 1}])
def test_rejects_invalid_envelopes(client, payload):
    assert client.post("/api/v1/predict", json=payload).status_code == 422


def test_batch_limits(settings, instances, client):
    assert client.post("/api/v1/predict", json={"instances": [instances[0]] * 1001}).status_code == 422
    with TestClient(create_app(replace(settings, max_batch_size=1))) as http:
        assert http.post("/api/v1/predict", json={"instances": instances[:2]}).status_code == 422


def test_body_limit_with_content_length(settings):
    with TestClient(create_app(replace(settings, max_request_bytes=64))) as http:
        response = http.post("/api/v1/predict", content=b"x" * 65)
        assert response.status_code == 413
        assert response.json()["request_id"] == response.headers["x-request-id"]


def test_body_limit_with_fragmented_transfer(settings):
    app = create_app(replace(settings, max_request_bytes=64))
    chunks = iter([
        {"type": "http.request", "body": b"x" * 40, "more_body": True},
        {"type": "http.request", "body": b"x" * 25, "more_body": False},
    ])
    messages = []

    async def receive():
        return next(chunks)

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "POST", "scheme": "http", "path": "/api/v1/predict", "raw_path": b"/api/v1/predict",
        "query_string": b"", "headers": [(b"transfer-encoding", b"chunked")],
        "server": ("test", 80), "client": ("test", 123), "root_path": "",
    }
    asyncio.run(app(scope, receive, send))
    assert messages[0]["status"] == 413
    assert json.loads(messages[1]["body"])["request_id"]


def test_readiness_without_lifespan(settings):
    http = TestClient(create_app(settings))
    assert http.get("/health/live").status_code == 200
    assert http.get("/health/ready").status_code == 503


def test_startup_fails_if_artifact_missing(settings, tmp_path):
    with pytest.raises(FileNotFoundError):
        with TestClient(create_app(replace(settings, model_path=tmp_path / "missing.joblib"))):
            pass


@pytest.mark.parametrize("change", ["hash", "package", "schema", "classes", "python"])
def test_startup_rejects_inconsistent_manifest(settings, tmp_path, change):
    manifest = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    if change == "hash":
        manifest["model_sha256"] = "0" * 64
    elif change == "package":
        manifest["packages"]["scikit-learn"] = "0.0.0"
    elif change == "schema":
        manifest["features"] = list(reversed(manifest["features"]))
    elif change == "classes":
        manifest["classes"] = list(reversed(manifest["classes"]))
    else:
        manifest["python_version"] = "0.0.0"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        with TestClient(create_app(replace(settings, manifest_path=path))):
            pass


def test_inference_error_is_sanitized(settings, instances, monkeypatch, caplog):
    def broken_predict(*args):
        raise RuntimeError("detalle interno que no debe salir")

    monkeypatch.setattr("deploy.web.api.main.predict_probabilities", broken_predict)
    with TestClient(create_app(settings)) as http:
        response = http.post("/api/v1/predict", json={"instances": instances[:1]})
    assert response.status_code == 500
    assert "detalle interno" not in response.text
    assert "detalle interno" not in caplog.text
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_logs_include_operation_metadata_without_rows(client, instances, caplog):
    response = client.post("/api/v1/predict", json={"instances": instances[:1]})
    logs = [json.loads(record.message) for record in caplog.records if record.message.startswith("{")]
    log = next(entry for entry in logs if entry["request_id"] == response.json()["request_id"])
    assert log["batch_size"] == 1
    assert log["status"] == 200
    assert log["model_version"] == response.json()["model_version"]
    assert log["latency_ms"] >= 0
    assert "Area" not in caplog.text


def test_saved_serving_artifact_matches_manifest(settings):
    manifest = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    assert hashlib.sha256(settings.model_path.read_bytes()).hexdigest() == manifest["model_sha256"]
    for name, expected in manifest["training"]["source_sha256"].items():
        source = Path(name).read_text(encoding="utf-8").encode("utf-8")
        assert hashlib.sha256(source).hexdigest() == expected
