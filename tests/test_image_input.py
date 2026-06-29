from __future__ import annotations

import pytest

from yolo_image_gateway.openai_compat.errors import GatewayError
from yolo_image_gateway.openai_compat.schemas import (
    ChatMessage,
    ChatMessageImageContent,
    ChatMessageImageURL,
    ChatMessageTextContent,
)
from yolo_image_gateway.vision.image_input import extract_single_image, parse_image_data_url

from .conftest import make_data_url


def test_parse_valid_png_data_url() -> None:
    decoded = parse_image_data_url(make_data_url("PNG"), max_image_bytes=1024 * 1024)

    assert decoded.mime_type == "image/png"
    assert decoded.width == 2
    assert decoded.height == 2
    assert decoded.byte_length > 0


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/image.png",
        "https://example.com/image.png",
        "file:///tmp/image.png",
        "/tmp/image.png",
    ],
)
def test_rejects_non_data_urls(url: str) -> None:
    with pytest.raises(GatewayError) as exc_info:
        parse_image_data_url(url, max_image_bytes=1024 * 1024)

    assert exc_info.value.status_code == 400


def test_rejects_invalid_base64() -> None:
    with pytest.raises(GatewayError) as exc_info:
        parse_image_data_url("data:image/png;base64,not-base64!", max_image_bytes=1024 * 1024)

    assert exc_info.value.code == "invalid_image_base64"


def test_rejects_unsupported_mime_type() -> None:
    payload = "data:image/gif;base64,R0lGODlhAQABAIAAAAUEBA=="

    with pytest.raises(GatewayError) as exc_info:
        parse_image_data_url(payload, max_image_bytes=1024 * 1024)

    assert exc_info.value.code == "unsupported_image_mime_type"


def test_extract_single_image_requires_exactly_one_image() -> None:
    message = ChatMessage(
        role="user",
        content=[ChatMessageTextContent(text="hello")],
    )

    with pytest.raises(GatewayError) as exc_info:
        extract_single_image([message], max_image_bytes=1024 * 1024)

    assert exc_info.value.code == "invalid_image_count"


def test_extract_single_image_validates_and_decodes() -> None:
    message = ChatMessage(
        role="user",
        content=[
            ChatMessageTextContent(text="detect"),
            ChatMessageImageContent(image_url=ChatMessageImageURL(url=make_data_url("JPEG"))),
        ],
    )

    decoded = extract_single_image([message], max_image_bytes=1024 * 1024)

    assert decoded.mime_type == "image/jpeg"
    assert decoded.width == 2
    assert decoded.height == 2
