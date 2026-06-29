"""FastAPI application factory and module-level app."""

from __future__ import annotations

import time

from fastapi import FastAPI

from .api.chat_completions import router as chat_completions_router
from .api.health import router as health_router
from .api.models import router as models_router
from .config import Settings
from .openai_compat.errors import GatewayError, gateway_error_handler
from .vision.detector import Detector, create_detector


def create_app(
    settings: Settings | None = None,
    detector: Detector | None = None,
) -> FastAPI:
    settings = settings or Settings()
    detector = detector or create_detector(settings)

    app = FastAPI(title="YOLO Image Gateway", version="0.0.0")
    app.state.settings = settings
    app.state.detector = detector
    app.state.started_at = int(time.time())

    app.add_exception_handler(GatewayError, gateway_error_handler)
    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(chat_completions_router)
    return app


app = create_app()
