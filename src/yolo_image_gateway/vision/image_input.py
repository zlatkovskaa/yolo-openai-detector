"""Base64 image data URL parsing and validation."""

from __future__ import annotations

import base64
from binascii import Error as BinasciiError
from io import BytesIO
from urllib.parse import urlsplit

from PIL import Image, UnidentifiedImageError

from ..openai_compat.errors import GatewayError
from ..openai_compat.schemas import ChatMessage
from .schemas import DecodedImage

SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def extract_single_image(messages: list[ChatMessage], max_image_bytes: int) -> DecodedImage:
    if len(messages) != 1:
        raise GatewayError(
            status_code=400,
            message="Exactly one user message with a single image is required.",
            code="invalid_message_count",
            param="messages",
        )

    message = messages[0]
    if message.role != "user":
        raise GatewayError(
            status_code=400,
            message="The request must contain a single user message.",
            code="invalid_message_role",
            param="messages",
        )

    image_items = [item for item in message.content if item.type == "image_url"]
    if len(image_items) != 1:
        raise GatewayError(
            status_code=400,
            message="Exactly one image data URL is required.",
            code="invalid_image_count",
            param="messages",
        )

    url = image_items[0].image_url.url
    return parse_image_data_url(url, max_image_bytes=max_image_bytes)


def parse_image_data_url(url: str, max_image_bytes: int) -> DecodedImage:
    scheme = urlsplit(url).scheme.lower()
    if scheme and scheme != "data":
        raise GatewayError(
            status_code=400,
            message="Only base64 data URLs are supported.",
            code="unsupported_image_url_scheme",
            param="messages",
        )

    if not url.startswith("data:"):
        raise GatewayError(
            status_code=400,
            message="Only base64 data URLs are supported.",
            code="invalid_image_url",
            param="messages",
        )

    header, separator, payload = url.partition(",")
    if not separator:
        raise GatewayError(
            status_code=400,
            message="The image data URL is missing a base64 payload.",
            code="invalid_image_url",
            param="messages",
        )

    metadata = header.removeprefix("data:")
    mime_type, *parameters = metadata.split(";")
    if len(parameters) != 1 or parameters[0].lower() != "base64":
        raise GatewayError(
            status_code=400,
            message="Only base64-encoded image data URLs are supported.",
            code="invalid_image_url",
            param="messages",
        )

    mime_type = mime_type.lower()
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise GatewayError(
            status_code=400,
            message="Unsupported image MIME type.",
            code="unsupported_image_mime_type",
            param="messages",
        )

    try:
        decoded = base64.b64decode(payload, validate=True)
    except (BinasciiError, ValueError) as exc:
        raise GatewayError(
            status_code=400,
            message="The image payload is not valid base64.",
            code="invalid_image_base64",
            param="messages",
        ) from exc

    if len(decoded) > max_image_bytes:
        raise GatewayError(
            status_code=413,
            message="The decoded image exceeds the maximum allowed size.",
            code="image_too_large",
            param="messages",
        )

    try:
        with Image.open(BytesIO(decoded)) as image:
            image.load()
            width, height = image.size
            format_name = image.format.lower() if image.format else None
    except UnidentifiedImageError as exc:
        raise GatewayError(
            status_code=400,
            message="The decoded payload is not a valid image.",
            code="invalid_image_payload",
            param="messages",
        ) from exc

    return DecodedImage(
        data=decoded,
        mime_type=mime_type,
        width=width,
        height=height,
        format=format_name,
        byte_length=len(decoded),
    )
