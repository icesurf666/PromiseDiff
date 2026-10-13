from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .archives import ArchiveError, unpack_pdfs
from .documents import DocumentError, enforce_collection_limits, inspect_pdf
from .llm_client import ModelError, ModelTimeout, ModelUnavailable, OllamaClient
from .service import analyze

MAX_UPLOAD = 12 * 1024 * 1024
MAX_DESCRIPTION = 10_000
app = FastAPI(title="PromiseDiff", docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=[origin for origin in __import__("os").getenv("CORS_ORIGINS", "http://localhost:5173").split(",")], allow_methods=["GET", "POST"], allow_headers=["content-type"])


@app.get("/api/health")
async def health() -> dict[str, bool | str]:
    client = OllamaClient()
    return {"status": "ok", "model_ready": await client.ready()}


@app.post("/api/analyze")
async def analyze_product(description: str = Form(...), file: UploadFile = File(...)):  # noqa: B008
    if not description.strip() or len(description) > MAX_DESCRIPTION:
        raise HTTPException(422, "Description must be between 1 and 10,000 characters")
    payload = await file.read(MAX_UPLOAD + 1)
    if len(payload) > MAX_UPLOAD:
        raise HTTPException(413, "Upload exceeds the 12 MB limit")
    name = file.filename or "upload"
    try:
        if payload.startswith(b"%PDF"):
            members = [(name, payload)]
        elif payload.startswith(b"PK"):
            members = unpack_pdfs(payload)
        else:
            raise DocumentError("Upload must be a PDF or ZIP containing PDFs")
        documents = [inspect_pdf(filename, content) for filename, content in members]
        enforce_collection_limits(documents)
    except (ArchiveError, DocumentError) as exc:
        raise HTTPException(400, str(exc)) from exc
    try:
        return await analyze(description, documents, OllamaClient())
    except ModelUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    except ModelTimeout as exc:
        raise HTTPException(504, str(exc)) from exc
    except ModelError as exc:
        raise HTTPException(503, str(exc)) from exc
