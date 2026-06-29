from __future__ import annotations

import pytest

from yolo_image_gateway.openai_compat.errors import GatewayError
from yolo_image_gateway.vision.detector import (
    UltralyticsYOLODetector,
    convert_ultralytics_results,
)
from yolo_image_gateway.vision.image_input import parse_image_data_url
from yolo_image_gateway.vision.schemas import BoundingBox

from .conftest import make_data_url


class FakeArray:
    def __init__(self, value):
        self.value = value

    def tolist(self):
        return self.value


class FakeBoxes:
    def __init__(self, xyxy, cls, conf):
        self.xyxy = FakeArray(xyxy)
        self.cls = FakeArray(cls)
        self.conf = FakeArray(conf)


class FakeResult:
    def __init__(self, names, boxes):
        self.names = names
        self.boxes = boxes


class FakeModel:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def predict(self, **kwargs):
        self.calls.append(kwargs)
        return self.results


def test_convert_ultralytics_results_maps_fields() -> None:
    results = [
        FakeResult(
            names={3: "truck"},
            boxes=FakeBoxes(
                xyxy=[[10.0, 20.0, 30.0, 40.0]],
                cls=[3],
                conf=[0.87],
            ),
        )
    ]

    detections = convert_ultralytics_results(results)

    assert len(detections) == 1
    detection = detections[0]
    assert detection.label == "truck"
    assert detection.class_id == 3
    assert detection.confidence == pytest.approx(0.87)
    assert detection.box == BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0)


def test_detector_uses_cpu_prediction_settings_and_converts_results() -> None:
    image = parse_image_data_url(make_data_url("PNG"), max_image_bytes=1024 * 1024)
    model = FakeModel(
        [
            FakeResult(
                names=["person"],
                boxes=FakeBoxes(
                    xyxy=[[12.0, 34.0, 56.0, 78.0]],
                    cls=[0],
                    conf=[0.91],
                ),
            )
        ]
    )
    detector = UltralyticsYOLODetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.33,
        iou_threshold=0.44,
        image_size=320,
        device="cpu",
        model_loader=lambda _: model,
    )

    detections = detector.detect(image)

    assert detections[0].label == "person"
    assert detections[0].box == BoundingBox(x1=12.0, y1=34.0, x2=56.0, y2=78.0)
    assert len(model.calls) == 1
    call = model.calls[0]
    assert call["device"] == "cpu"
    assert call["conf"] == pytest.approx(0.33)
    assert call["iou"] == pytest.approx(0.44)
    assert call["imgsz"] == 320
    assert call["verbose"] is False
    assert call["source"].mode == "RGB"
    assert call["source"].size == (2, 2)


def test_detector_model_load_failure_is_controlled() -> None:
    image = parse_image_data_url(make_data_url("PNG"), max_image_bytes=1024 * 1024)

    def loader(_: str) -> object:
        raise FileNotFoundError("missing model weights")

    detector = UltralyticsYOLODetector(
        model_path="missing.pt",
        model_loader=loader,
    )

    with pytest.raises(GatewayError) as exc_info:
        detector.detect(image)

    assert exc_info.value.code == "detector_model_load_failed"
