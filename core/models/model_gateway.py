import json
import logging
import time
from pathlib import Path

from ollama import AsyncClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REGISTRY_FILE = (
    PROJECT_ROOT
    / "core"
    / "models"
    / "model_registry.json"
)


class ModelGateway:
    def __init__(self):
        self.logger = logging.getLogger("shaz.model_gateway")
        self.registry = self._load_registry()
        self.client = AsyncClient()

    def _load_registry(self):
        with REGISTRY_FILE.open(
            "r",
            encoding="utf-8",
        ) as registry_file:
            return json.load(registry_file)

    def _resolve_model(self, model):
        model_key = (
            model
            or self.registry["default_policy"]
        )

        model_config = self.registry["models"].get(
            model_key
        )

        if model_config is None:
            raise ValueError(
                f"Unknown model policy: {model_key}"
            )

        return model_key, model_config

    async def generate(
        self,
        messages,
        model=None,
        stream=False,
        tools=None,
    ):
        model_key, model_config = (
            self._resolve_model(model)
        )

        backend = model_config["backend"]
        model_name = model_config["model"]

        if backend != "ollama":
            raise ValueError(
                f"Unsupported backend: {backend}"
            )

        started_at = time.perf_counter()

        self.logger.info(
            "Model request started | policy=%s model=%s stream=%s",
            model_key,
            model_name,
            stream,
        )

        try:
            response = await self.client.chat(
                model=model_name,
                messages=messages,
                tools=tools,
                stream=stream,
            )

            if stream:
                return self._stream_response(
                    response=response,
                    model_key=model_key,
                    model_name=model_name,
                    started_at=started_at,
                )

            elapsed = (
                time.perf_counter()
                - started_at
            )

            self.logger.info(
                "Model request completed | policy=%s model=%s latency=%.2fs",
                model_key,
                model_name,
                elapsed,
            )

            return response

        except Exception:
            elapsed = (
                time.perf_counter()
                - started_at
            )

            self.logger.exception(
                "Model request failed | policy=%s model=%s latency=%.2fs",
                model_key,
                model_name,
                elapsed,
            )

            raise

    async def _stream_response(
        self,
        response,
        model_key,
        model_name,
        started_at,
    ):
        try:
            async for chunk in response:
                yield chunk

            elapsed = (
                time.perf_counter()
                - started_at
            )

            self.logger.info(
                "Model stream completed | policy=%s model=%s latency=%.2fs",
                model_key,
                model_name,
                elapsed,
            )

        except Exception:
            elapsed = (
                time.perf_counter()
                - started_at
            )

            self.logger.exception(
                "Model stream failed | policy=%s model=%s latency=%.2fs",
                model_key,
                model_name,
                elapsed,
            )

            raise
