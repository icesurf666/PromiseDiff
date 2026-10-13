from fastapi.testclient import TestClient

from app import main
from app.llm_client import ModelError, ModelTimeout, ModelUnavailable
from app.main import app

client = TestClient(app)


def test_health_has_truthful_shape():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert isinstance(response.json()["model_ready"], bool)


def test_rejects_unsupported_upload_before_model_inference():
    response = client.post(
        "/api/analyze",
        data={"description": "Includes a planner."},
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF or ZIP" in response.json()["detail"]


def test_rejects_empty_and_oversized_descriptions():
    file = {"file": ("x.pdf", b"%PDF-1.7", "application/pdf")}
    assert client.post("/api/analyze", data={"description": " "}, files=file).status_code == 422
    response = client.post("/api/analyze", data={"description": "x" * 10_001}, files=file)
    assert response.status_code == 422


def valid_pdf() -> bytes:
    return (b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n%%EOF")


def test_translates_model_unavailable_and_timeout(monkeypatch):
    class Unavailable:
        async def structured(self, *_):
            raise ModelUnavailable("offline")

    class Timeout:
        async def structured(self, *_):
            raise ModelTimeout("slow")

    class Malformed:
        async def structured(self, *_):
            raise ModelError("invalid output")

    payload = {"description": "Includes a planner."}
    files = {"file": ("x.pdf", valid_pdf(), "application/pdf")}
    monkeypatch.setattr(main, "OllamaClient", Unavailable)
    assert client.post("/api/analyze", data=payload, files=files).status_code == 503
    monkeypatch.setattr(main, "OllamaClient", Timeout)
    assert client.post("/api/analyze", data=payload, files=files).status_code == 504
    monkeypatch.setattr(main, "OllamaClient", Malformed)
    assert client.post("/api/analyze", data=payload, files=files).status_code == 503
