from __future__ import annotations

import base64
from collections.abc import Iterable
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from yolo_image_gateway.config import Settings
from yolo_image_gateway.main import create_app
from yolo_image_gateway.vision.schemas import BoundingBox, Detection


class FakeDetector:
    backend_name = "fake"
    device = "cpu"

    def __init__(self, detections: Iterable[Detection] | None = None) -> None:
        self.detections = list(detections or [])
        self.seen_images = []

    def detect(self, image):
        self.seen_images.append(image)
        return list(self.detections)


def make_image_bytes(format_name: str, size: tuple[int, int] = (2, 2)) -> bytes:
    image = Image.new("RGB", size, color=(255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format=format_name)
    return buffer.getvalue()


def make_data_url(format_name: str) -> str:
    mime_map = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
    }
    payload = base64.b64encode(make_image_bytes(format_name)).decode("ascii")
    return f"data:{mime_map[format_name]};base64,{payload}"


@pytest.fixture
def settings() -> Settings:
    return Settings(
        api_key="test-local-key",
        model_id="yolo-cpu-detector",
        max_image_bytes=10 * 1024 * 1024,
        device="cpu",
    )


@pytest.fixture
def fake_detector() -> FakeDetector:
    return FakeDetector(
        detections=[
            Detection(
                label="person",
                class_id=0,
                confidence=0.91,
                box=BoundingBox(x1=120.0, y1=80.0, x2=340.0, y2=500.0),
            )
        ]
    )


@pytest.fixture
def client(settings: Settings, fake_detector: FakeDetector) -> TestClient:
    app = create_app(settings=settings, detector=fake_detector)
    return TestClient(app)


@pytest.fixture
def auth_headers(settings: Settings) -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.api_key}"}
