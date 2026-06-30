from __future__ import annotations

import pytest

from examples.openai_client_single_image import (
    build_chat_completion_request,
    parse_completion_content,
)
from scripts.encode_image_data_url import encode_image_data_url, infer_image_mime_type

from .conftest import make_image_bytes


@pytest.mark.parametrize(
    ("suffix", "format_name", "expected_mime_type"),
    [
        (".jpg", "JPEG", "image/jpeg"),
        (".jpeg", "JPEG", "image/jpeg"),
        (".png", "PNG", "image/png"),
        (".webp", "WEBP", "image/webp"),
    ],
)
def test_encode_image_data_url_detects_supported_mime_types(
    tmp_path,
    suffix: str,
    format_name: str,
    expected_mime_type: str,
) -> None:
    image_path = tmp_path / f"sample{suffix}"
    image_path.write_bytes(make_image_bytes(format_name))

    assert infer_image_mime_type(image_path) == expected_mime_type

    data_url = encode_image_data_url(image_path)
    assert data_url.startswith(f"data:{expected_mime_type};base64,")


def test_encode_image_data_url_rejects_unsupported_extension(tmp_path) -> None:
    image_path = tmp_path / "sample.gif"
    image_path.write_bytes(make_image_bytes("PNG"))

    with pytest.raises(ValueError, match="Unsupported image type"):
        infer_image_mime_type(image_path)

    with pytest.raises(ValueError, match="Unsupported image type"):
        encode_image_data_url(image_path)


def test_build_chat_completion_request_contains_exactly_one_image() -> None:
    payload = build_chat_completion_request("data:image/png;base64,abc123")
    content = payload["messages"][0]["content"]

    assert payload["model"] == "yolo-cpu-detector"
    assert len(content) == 2
    assert sum(1 for item in content if item["type"] == "image_url") == 1
    assert content[1]["image_url"]["url"] == "data:image/png;base64,abc123"


def test_parse_completion_content_handles_json_string_content() -> None:
    content = (
        '{"detections":[{"label":"person","class_id":0,"confidence":0.91,'
        '"box":{"x1":1.0,"y1":2.0,"x2":3.0,"y2":4.0}}],'
        '"image":{"width":640,"height":480},'
        '"runtime":{"backend":"ultralytics","device":"cpu"}}'
    )

    payload = parse_completion_content(content)

    assert payload["detections"][0]["label"] == "person"
    assert payload["image"]["width"] == 640
    assert payload["runtime"]["device"] == "cpu"
