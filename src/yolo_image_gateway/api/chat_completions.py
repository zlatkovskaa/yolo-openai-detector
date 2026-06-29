"""Chat completions endpoint."""

from __future__ import annotations

import re
import time
import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError

from ..auth import require_api_key
from ..openai_compat.errors import GatewayError
from ..openai_compat.schemas import (
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from ..vision.image_input import extract_single_image
from ..vision.schemas import Detection, DetectionResponseContent, ImageMetadata, RuntimeInfo

router = APIRouter()

UNSUPPORTED_REQUEST_INTENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\btrack(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\btracking\s+id(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bvideo\b", re.IGNORECASE),
    re.compile(r"\bsegmentation\b", re.IGNORECASE),
    re.compile(r"\bmasks?\b", re.IGNORECASE),
    re.compile(r"\bbackground\s+(?:processing|job(?:s)?|task(?:s)?)\b", re.IGNORECASE),
    re.compile(r"\bprocess(?:ing)?\s+in\s+background\b", re.IGNORECASE),
    re.compile(r"\basync\s+job(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bqueue(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bworker(?:s)?\b", re.IGNORECASE),
)


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: Request,
    _: None = Depends(require_api_key),
) -> ChatCompletionResponse:
    settings = request.app.state.settings

    try:
        payload = await request.json()
    except ValueError as exc:
        raise GatewayError(
            status_code=400,
            message="Request body must be valid JSON.",
            code="invalid_json",
            param="body",
        ) from exc

    try:
        chat_request = ChatCompletionRequest.model_validate(payload)
    except ValidationError as exc:
        raise GatewayError(
            status_code=400,
            message="Invalid chat completion request.",
            code="invalid_request",
            param="body",
        ) from exc

    if chat_request.model != settings.model_id:
        raise GatewayError(
            status_code=400,
            message="Unsupported model.",
            code="unsupported_model",
            param="model",
        )

    _reject_unsupported_request_intents(chat_request)
    image = extract_single_image(chat_request.messages, max_image_bytes=settings.max_image_bytes)
    detector = request.app.state.detector

    try:
        detections = [Detection.model_validate(detection) for detection in detector.detect(image)]
    except GatewayError:
        raise
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise GatewayError(
            status_code=500,
            message="The detector failed to process the image.",
            code="detector_error",
            error_type="server_error",
        ) from exc

    content = DetectionResponseContent(
        detections=detections,
        image=ImageMetadata(
            width=image.width,
            height=image.height,
            mime_type=image.mime_type,
            byte_length=image.byte_length,
            format=image.format,
        ),
        runtime=RuntimeInfo(
            backend=getattr(detector, "backend_name", "unknown"),
            device=getattr(detector, "device", settings.device),
        ),
    )

    return ChatCompletionResponse(
        id=f"chatcmpl-local-{uuid.uuid4().hex}",
        created=int(time.time()),
        model=chat_request.model,
        choices=[
            ChatCompletionChoice(
                message=ChatCompletionMessage(
                    content=content.model_dump_json(exclude_none=True),
                )
            )
        ],
    )


def _reject_unsupported_request_intents(chat_request: ChatCompletionRequest) -> None:
    request_text = "\n".join(
        item.text
        for message in chat_request.messages
        if message.role == "user"
        for item in message.content
        if item.type == "text"
    )
    if not request_text:
        return

    if any(pattern.search(request_text) for pattern in UNSUPPORTED_REQUEST_INTENT_PATTERNS):
        raise GatewayError(
            status_code=400,
            message=(
                "Unsupported request: v1 supports single-image object detection only. "
                "Tracking, video, segmentation, and background processing are not supported."
            ),
            code="unsupported_request_intent",
            param="messages",
        )
