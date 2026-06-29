"""Detector abstraction and Ultralytics-backed implementation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from io import BytesIO
from typing import Any, Protocol, runtime_checkable

from PIL import Image

from ..openai_compat.errors import GatewayError
from .schemas import BoundingBox, DecodedImage, Detection


@runtime_checkable
class Detector(Protocol):
    backend_name: str
    device: str

    def detect(self, image: DecodedImage) -> list[Detection]: ...


class UltralyticsYOLODetector:
    """CPU-first YOLO detector with lazy model loading."""

    backend_name = "ultralytics"

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        image_size: int = 640,
        device: str = "cpu",
        model_loader: Callable[[str], Any] | None = None,
    ) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.image_size = image_size
        self.device = device
        self._model_loader = model_loader
        self._model: Any | None = None

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        if self._model_loader is not None:
            try:
                self._model = self._model_loader(self.model_path)
            except GatewayError:
                raise
            except Exception as exc:  # pragma: no cover - defensive boundary
                raise GatewayError(
                    status_code=500,
                    message="The YOLO model could not be loaded.",
                    code="detector_model_load_failed",
                    error_type="server_error",
                ) from exc
            return self._model

        try:
            from ultralytics import YOLO
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise GatewayError(
                status_code=500,
                message="Ultralytics is not installed.",
                code="detector_dependency_missing",
                error_type="server_error",
            ) from exc

        try:
            self._model = YOLO(self.model_path)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise GatewayError(
                status_code=500,
                message="The YOLO model could not be loaded.",
                code="detector_model_load_failed",
                error_type="server_error",
            ) from exc

        return self._model

    def detect(self, image: DecodedImage) -> list[Detection]:
        model = self._load_model()

        try:
            with Image.open(BytesIO(image.data)) as pil_image:
                pil_image.load()
                source_image = pil_image.convert("RGB")
                results = model.predict(
                    source=source_image,
                    conf=self.confidence_threshold,
                    iou=self.iou_threshold,
                    imgsz=self.image_size,
                    device=self.device,
                    verbose=False,
                )
        except GatewayError:
            raise
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise GatewayError(
                status_code=500,
                message="The YOLO detector failed to process the image.",
                code="detector_prediction_failed",
                error_type="server_error",
            ) from exc

        return convert_ultralytics_results(results)


def create_detector(settings: Any) -> Detector:
    return UltralyticsYOLODetector(
        model_path=(
            getattr(settings, "model_path", None)
            or getattr(settings, "yolo_model", None)
            or "yolov8n.pt"
        ),
        confidence_threshold=settings.confidence_threshold,
        iou_threshold=settings.iou_threshold,
        image_size=settings.image_size,
        device=settings.device,
    )


def convert_ultralytics_results(results: Any) -> list[Detection]:
    """Convert Ultralytics-style results into project detection schemas."""

    detections: list[Detection] = []
    for result in _ensure_iterable(results):
        names = getattr(result, "names", None) or {}
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            continue

        xyxy_rows = _normalize_rows(getattr(boxes, "xyxy", None))
        class_ids = _normalize_scalars(getattr(boxes, "cls", None))
        confidences = _normalize_scalars(getattr(boxes, "conf", None))

        for index, coordinates in enumerate(xyxy_rows):
            if len(coordinates) != 4:
                continue

            class_id = _coerce_int(_value_at(class_ids, index))
            confidence = _coerce_float(_value_at(confidences, index))
            if class_id is None or confidence is None:
                continue

            detections.append(
                Detection(
                    label=_label_for_class(names, class_id),
                    class_id=class_id,
                    confidence=confidence,
                    box=BoundingBox(
                        x1=float(coordinates[0]),
                        y1=float(coordinates[1]),
                        x2=float(coordinates[2]),
                        y2=float(coordinates[3]),
                    ),
                )
            )

    return detections


def _ensure_iterable(results: Any) -> Iterable[Any]:
    if results is None:
        return []
    if isinstance(results, (list, tuple)):
        return results
    return [results]


def _normalize_rows(value: Any) -> list[list[float]]:
    if value is None:
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, list):
        value = list(value)
    if not value:
        return []
    if isinstance(value[0], (int, float)):
        return [list(value)]
    return [list(row) for row in value]


def _normalize_scalars(value: Any) -> list[Any]:
    if value is None:
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _value_at(values: list[Any], index: int) -> Any | None:
    if index >= len(values):
        return None
    return values[index]


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    if hasattr(value, "item"):
        value = value.item()
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    if hasattr(value, "item"):
        value = value.item()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _label_for_class(names: Any, class_id: int) -> str:
    if isinstance(names, dict):
        label = names.get(class_id)
    elif isinstance(names, list) and 0 <= class_id < len(names):
        label = names[class_id]
    else:
        label = None
    return str(label if label is not None else class_id)
