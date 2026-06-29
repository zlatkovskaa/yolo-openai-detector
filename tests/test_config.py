from __future__ import annotations

import pytest
from pydantic import ValidationError

from yolo_image_gateway.config import Settings


def test_settings_defaults_to_cpu() -> None:
    settings = Settings(api_key="test-local-key")

    assert settings.device == "cpu"
    assert settings.model_path == "yolov8n.pt"
    assert settings.confidence_threshold == 0.25
    assert settings.iou_threshold == 0.45
    assert settings.image_size == 640


def test_settings_rejects_non_cpu_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOLO_GATEWAY_DEVICE", "cuda")

    with pytest.raises(ValidationError) as exc_info:
        Settings(api_key="test-local-key")

    assert "Only the cpu device is supported" in str(exc_info.value)
