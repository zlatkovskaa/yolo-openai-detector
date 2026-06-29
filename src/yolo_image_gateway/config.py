"""Runtime configuration for the YOLO image gateway."""

from __future__ import annotations

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed application settings."""

    model_config = SettingsConfigDict(env_prefix="YOLO_GATEWAY_", extra="ignore")

    api_key: str = Field(default="")
    model_id: str = Field(default="yolo-cpu-detector")
    model_path: str = Field(default="yolov8n.pt")
    yolo_model: str | None = Field(default=None)
    max_image_bytes: int = Field(default=10 * 1024 * 1024)
    confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0)
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    image_size: int = Field(default=640, gt=0)
    device: str = Field(default="cpu")

    @model_validator(mode="after")
    def _apply_legacy_model_path(self) -> Settings:
        if self.yolo_model and self.model_path == "yolov8n.pt":
            self.model_path = self.yolo_model
        self.device = self.device.strip().lower()
        if self.device != "cpu":
            raise ValueError("Only the cpu device is supported in v1.")
        return self
