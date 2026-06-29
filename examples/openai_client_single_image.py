"""Run a single-image detection request through the local gateway."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # pragma: no cover - runtime convenience for direct execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.encode_image_data_url import encode_image_data_url

DEFAULT_BASE_URL = "http://127.0.0.1:8000/v1"
DEFAULT_MODEL_ID = "yolo-cpu-detector"
DEFAULT_PROMPT = "Detect objects in this image."


def build_chat_completion_request(
    image_data_url: str,
    model_id: str = DEFAULT_MODEL_ID,
    prompt: str = DEFAULT_PROMPT,
) -> dict[str, Any]:
    return {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            }
        ],
    }


def parse_completion_content(content: str) -> dict[str, Any]:
    return json.loads(content)


def format_summary(payload: dict[str, Any]) -> str:
    image = payload.get("image", {})
    detections = payload.get("detections", [])
    lines = [
        f"Image: {image.get('width', '?')}x{image.get('height', '?')}",
        f"Detections: {len(detections)}",
    ]
    for detection in detections:
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
    return "\n".join(lines)


def create_openai_client(base_url: str, api_key: str) -> Any:
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Call the local YOLO gateway using the OpenAI Python client.",
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
    base_url = os.getenv("YOLO_GATEWAY_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    api_key = os.getenv("YOLO_GATEWAY_API_KEY")
    model_id = os.getenv("YOLO_GATEWAY_MODEL_ID", DEFAULT_MODEL_ID)

    if not api_key:
        print("Error: set YOLO_GATEWAY_API_KEY to your local gateway key.", file=sys.stderr)
        return 1

    try:
        image_data_url = encode_image_data_url(args.image_path)
        client = create_openai_client(base_url=base_url, api_key=api_key)
        completion = client.chat.completions.create(
            model=model_id,
            messages=build_chat_completion_request(
                image_data_url=image_data_url,
                model_id=model_id,
                prompt=args.prompt,
            )["messages"],
        )
        content = completion.choices[0].message.content
        if content is None:
            raise ValueError("The gateway returned an empty assistant message.")
        payload = parse_completion_content(content)
    except Exception as exc:  # pragma: no cover - example CLI boundary
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(format_summary(payload))
    print("\nRaw JSON content:")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
