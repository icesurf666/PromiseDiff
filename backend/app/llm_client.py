from __future__ import annotations

import json
import os

import httpx
from pydantic import BaseModel, ValidationError


class ModelError(RuntimeError):
    pass


class ModelUnavailable(ModelError):
    pass


class ModelTimeout(ModelError):
    pass


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "45"))

    async def ready(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f"{self.base_url}/api/tags")
            return response.is_success and any(item.get("name") == self.model for item in response.json().get("models", []))
        except (httpx.HTTPError, ValueError):
            return False

    async def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        body = {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=body)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ModelTimeout("Ollama inference timed out") from exc
        except httpx.HTTPError as exc:
            raise ModelUnavailable("Ollama is unavailable or the configured model is missing") from exc
        try:
            return schema.model_validate(json.loads(response.json()["response"]))
        except (KeyError, ValueError, ValidationError) as exc:
            raise ModelError("Ollama returned invalid structured output") from exc
