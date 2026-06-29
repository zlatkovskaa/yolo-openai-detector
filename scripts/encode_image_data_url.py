"""Encode a local image file as a base64 data URL."""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

SUPPORTED_IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def infer_image_mime_type(image_path: Path) -> str:
    mime_type = SUPPORTED_IMAGE_MIME_TYPES.get(image_path.suffix.lower())
    if mime_type is None:
        raise ValueError("Unsupported image type. Use .jpg, .jpeg, .png, or .webp.")
    return mime_type


def encode_image_data_url(image_path: Path) -> str:
    if not image_path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    mime_type = infer_image_mime_type(image_path)
    raw_bytes = image_path.read_bytes()
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encode a local image file as a base64 data URL.",
    )
    parser.add_argument(
        "image_path",
        type=Path,
        help="Path to a .jpg, .jpeg, .png, or .webp file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(encode_image_data_url(args.image_path))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
