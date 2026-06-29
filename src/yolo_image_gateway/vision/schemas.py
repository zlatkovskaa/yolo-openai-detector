"""Vision data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    label: str
    class_id: int
    confidence: float
    box: BoundingBox


class DecodedImage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: bytes
    mime_type: str
    width: int
    height: int
    format: str | None = None
    byte_length: int = Field(default=0)


class ImageMetadata(BaseModel):
    width: int
    height: int
    mime_type: str | None = None
    byte_length: int | None = None
    format: str | None = None


class RuntimeInfo(BaseModel):
    backend: str
    device: str


class DetectionResponseContent(BaseModel):
    detections: list[Detection] = Field(default_factory=list)
    image: ImageMetadata | None = None
    runtime: RuntimeInfo | None = None
