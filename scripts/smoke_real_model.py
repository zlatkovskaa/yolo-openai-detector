"""Manual smoke validation for a real local YOLO model file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # pragma: no cover - runtime convenience for direct execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.openai_client_single_image import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL_ID,
    DEFAULT_PROMPT,
    build_chat_completion_request,
    create_openai_client,
    parse_completion_content,
)
from scripts.encode_image_data_url import encode_image_data_url


@dataclass(frozen=True)
class SmokeConfig:
    model_path: Path
    api_key: str
    base_url: str
    model_id: str


def build_smoke_request(
    image_data_url: str,
    model_id: str = DEFAULT_MODEL_ID,
    prompt: str = DEFAULT_PROMPT,
) -> dict[str, Any]:
    return build_chat_completion_request(
        image_data_url=image_data_url,
        model_id=model_id,
        prompt=prompt,
    )


def load_smoke_config() -> SmokeConfig:
    model_path_value = os.getenv("YOLO_GATEWAY_MODEL_PATH")
    if not model_path_value:
        raise ValueError("Set YOLO_GATEWAY_MODEL_PATH to a local YOLO model file.")

    model_path = Path(model_path_value).expanduser()
    if not model_path.is_file():
        raise FileNotFoundError(
            f"YOLO_GATEWAY_MODEL_PATH does not point to an existing file: {model_path}"
        )

    api_key = os.getenv("YOLO_GATEWAY_API_KEY")
    if not api_key:
        raise ValueError("Set YOLO_GATEWAY_API_KEY to your local gateway key.")

    base_url = (os.getenv("YOLO_GATEWAY_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    model_id = os.getenv("YOLO_GATEWAY_MODEL_ID") or DEFAULT_MODEL_ID
    return SmokeConfig(
        model_path=model_path,
        api_key=api_key,
        base_url=base_url,
        model_id=model_id,
    )


def create_gateway_client(base_url: str, api_key: str) -> Any:
    try:
        return create_openai_client(base_url=base_url, api_key=api_key)
    except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(
            "The OpenAI Python client is not installed. Install the dev dependencies first."
        ) from exc


def request_smoke_completion(
    client: Any,
    *,
    base_url: str,
    model_id: str,
    messages: list[dict[str, Any]],
) -> Any:
    try:
        return client.chat.completions.create(model=model_id, messages=messages)
    except Exception as exc:  # pragma: no cover - network boundary
        if exc.__class__.__name__ == "APIConnectionError" or "connection" in str(exc).lower():
            raise RuntimeError(f"Unable to reach local gateway at {base_url}: {exc}") from exc
        raise


def parse_smoke_completion(completion: Any) -> dict[str, Any]:
    choices = getattr(completion, "choices", None)
    if not choices:
        raise ValueError("Unexpected completion response shape: missing choices[0].")

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    if not isinstance(content, str):
        raise ValueError(
            "Unexpected completion response shape: "
            "choices[0].message.content must be a JSON string."
        )

    try:
        payload = parse_completion_content(content)
    except ValueError as exc:
        raise ValueError(
            "The gateway returned invalid JSON in choices[0].message.content."
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError(
            "Unexpected completion response shape: content must decode to a JSON object."
        )
    return payload


def validate_smoke_payload(payload: dict[str, Any]) -> None:
    image = payload.get("image")
    detections = payload.get("detections")
    runtime = payload.get("runtime")
    if (
        not isinstance(image, dict)
        or not isinstance(detections, list)
        or not isinstance(runtime, dict)
    ):
        raise ValueError(
            "Unexpected payload shape: expected detections, image metadata, and runtime fields."
        )

    if runtime.get("device") != "cpu":
        raise ValueError(
            f"Unexpected runtime device: {runtime.get('device')!r}. CPU mode is required."
        )


def format_smoke_report(
    payload: dict[str, Any],
    *,
    model_id: str,
    base_url: str,
    model_path: Path,
) -> str:
    image = payload["image"]
    runtime = payload["runtime"]
    detections = payload["detections"]

    lines = [
        f"Model ID: {model_id}",
        f"Model path: {model_path}",
        f"Base URL: {base_url}",
        (
            "Image: {width}x{height} ({mime_type}, {byte_length} bytes)".format(
                width=image.get("width", "?"),
                height=image.get("height", "?"),
                mime_type=image.get("mime_type", "unknown"),
                byte_length=image.get("byte_length", "?"),
            )
        ),
        "Runtime: {backend} / {device}".format(
            backend=runtime.get("backend", "unknown"),
            device=runtime.get("device", "unknown"),
        ),
        f"Detections: {len(detections)}",
    ]

    if detections:
        lines.append("Top detections:")
        for detection in detections[:5]:
            box = detection.get("box", {})
            lines.append(
                "- {label} (class {class_id}, confidence {confidence:.3f}) "
                "[{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}]".format(
                    label=detection.get("label", "unknown"),
                    class_id=detection.get("class_id", "?"),
                    confidence=float(detection.get("confidence", 0.0)),
                    x1=float(box.get("x1", 0.0)),
                    y1=float(box.get("y1", 0.0)),
                    x2=float(box.get("x2", 0.0)),
                    y2=float(box.get("y2", 0.0)),
                )
            )
    else:
        lines.append("Top detections: none")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smoke test the local gateway against a real local YOLO model file.",
    )
    parser.add_argument(
        "image_path",
        type=Path,
        help="Path to a local .jpg, .jpeg, .png, or .webp image.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="User text prompt sent with the image.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        config = load_smoke_config()
        image_path = args.image_path.expanduser()
        image_data_url = encode_image_data_url(image_path)
        client = create_gateway_client(base_url=config.base_url, api_key=config.api_key)
        completion = request_smoke_completion(
            client,
            base_url=config.base_url,
            model_id=config.model_id,
            messages=build_smoke_request(
                image_data_url=image_data_url,
                model_id=config.model_id,
                prompt=args.prompt,
            )["messages"],
        )
        payload = parse_smoke_completion(completion)
        validate_smoke_payload(payload)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        format_smoke_report(
            payload,
            model_id=config.model_id,
            base_url=config.base_url,
            model_path=config.model_path,
        )
    )
    print("\nRaw JSON content:")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
