from __future__ import annotations

import json

import pytest

from .conftest import FakeDetector, make_data_url


def _request_payload(
    image_url: str,
    text: str = "Detect objects in this image.",
) -> dict[str, object]:
    return {
        "model": "yolo-cpu-detector",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
    }


def test_chat_completion_rejects_no_image(client, auth_headers) -> None:
    payload = {
        "model": "yolo-cpu-detector",
        "messages": [{"role": "user", "content": [{"type": "text", "text": "hello"}]}],
    }

    response = client.post("/v1/chat/completions", headers=auth_headers, json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image_count"


def test_chat_completion_rejects_multiple_images(client, auth_headers) -> None:
    payload = {
        "model": "yolo-cpu-detector",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": make_data_url("PNG")}},
                    {"type": "image_url", "image_url": {"url": make_data_url("JPEG")}},
                ],
            }
        ],
    }

    response = client.post("/v1/chat/completions", headers=auth_headers, json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image_count"


@pytest.mark.parametrize(
    "text",
    [
        "Track these objects across frames.",
        "Please do video analysis on this image.",
        "Use segmentation masks for the objects.",
        "Run this as a background processing job.",
        "Send this to a queue worker as an async job.",
    ],
)
def test_chat_completion_rejects_unsupported_request_intents(
    client,
    auth_headers,
    text: str,
) -> None:
    response = client.post(
        "/v1/chat/completions",
        headers=auth_headers,
        json=_request_payload(make_data_url("PNG"), text=text),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "unsupported_request_intent"
    assert "single-image object detection only" in body["error"]["message"]


def test_chat_completion_accepts_background_phrasing(
    client,
    auth_headers,
    fake_detector: FakeDetector,
) -> None:
    response = client.post(
        "/v1/chat/completions",
        headers=auth_headers,
        json=_request_payload(
            make_data_url("PNG"),
            text="Detect objects in the background of this image.",
        ),
    )

    assert response.status_code == 200
    assert fake_detector.seen_images


@pytest.mark.parametrize(
    "url, expected_code",
    [
        ("http://example.com/image.png", "unsupported_image_url_scheme"),
        ("https://example.com/image.png", "unsupported_image_url_scheme"),
        ("file:///tmp/image.png", "unsupported_image_url_scheme"),
        ("not-a-url", "invalid_image_url"),
        ("data:image/png;base64,not-base64!", "invalid_image_base64"),
        ("data:image/gif;base64,R0lGODlhAQABAIAAAAUEBA==", "unsupported_image_mime_type"),
    ],
)
def test_chat_completion_rejects_invalid_image_input(
    client,
    auth_headers,
    url: str,
    expected_code: str,
) -> None:
    response = client.post(
        "/v1/chat/completions",
        headers=auth_headers,
        json=_request_payload(url),
    )

    assert response.status_code in {400, 413}
    assert response.json()["error"]["code"] == expected_code


@pytest.mark.parametrize("format_name", ["PNG", "JPEG", "WEBP"])
def test_chat_completion_accepts_valid_base64_images(
    client,
    auth_headers,
    fake_detector: FakeDetector,
    format_name: str,
) -> None:
    response = client.post(
        "/v1/chat/completions",
        headers=auth_headers,
        json=_request_payload(make_data_url(format_name)),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["model"] == "yolo-cpu-detector"
    assert body["choices"][0]["message"]["role"] == "assistant"

    content = body["choices"][0]["message"]["content"]
    assert isinstance(content, str)

    decoded = json.loads(content)
    assert decoded["image"]["width"] == 2
    assert decoded["image"]["height"] == 2
    assert decoded["detections"][0]["label"] == "person"
    assert decoded["detections"][0]["box"] == {
        "x1": 120.0,
        "y1": 80.0,
        "x2": 340.0,
        "y2": 500.0,
    }
    assert fake_detector.seen_images
    assert fake_detector.seen_images[-1].mime_type in {"image/png", "image/jpeg", "image/webp"}


def test_fake_detector_output_appears_in_response_content(client, auth_headers) -> None:
    response = client.post(
        "/v1/chat/completions",
        headers=auth_headers,
        json=_request_payload(make_data_url("PNG")),
    )

    content = response.json()["choices"][0]["message"]["content"]
    decoded = json.loads(content)

    assert decoded["detections"][0]["label"] == "person"
    assert decoded["detections"][0]["class_id"] == 0
    assert decoded["runtime"]["backend"] == "fake"
