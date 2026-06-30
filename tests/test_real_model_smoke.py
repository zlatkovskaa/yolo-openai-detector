from __future__ import annotations

from types import SimpleNamespace

import pytest

import scripts.smoke_real_model as smoke


def test_load_smoke_config_requires_model_path(monkeypatch) -> None:
    monkeypatch.delenv("YOLO_GATEWAY_MODEL_PATH", raising=False)
    monkeypatch.setenv("YOLO_GATEWAY_API_KEY", "local-dev-key")

    with pytest.raises(ValueError, match="YOLO_GATEWAY_MODEL_PATH"):
        smoke.load_smoke_config()


def test_load_smoke_config_requires_existing_model_path(tmp_path, monkeypatch) -> None:
    missing_model = tmp_path / "missing.pt"
    monkeypatch.setenv("YOLO_GATEWAY_MODEL_PATH", str(missing_model))
    monkeypatch.setenv("YOLO_GATEWAY_API_KEY", "local-dev-key")

    with pytest.raises(FileNotFoundError, match="YOLO_GATEWAY_MODEL_PATH"):
        smoke.load_smoke_config()


def test_main_rejects_missing_image_path(tmp_path, monkeypatch, capsys) -> None:
    model_path = tmp_path / "model.pt"
    model_path.write_text("placeholder")
    monkeypatch.setenv("YOLO_GATEWAY_MODEL_PATH", str(model_path))
    monkeypatch.setenv("YOLO_GATEWAY_API_KEY", "local-dev-key")

    exit_code = smoke.main(["missing-image.png"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Image file not found" in captured.err


def test_main_rejects_missing_api_key(tmp_path, monkeypatch, capsys) -> None:
    model_path = tmp_path / "model.pt"
    model_path.write_text("placeholder")
    image_path = tmp_path / "image.png"
    image_path.write_bytes(b"placeholder")
    monkeypatch.setenv("YOLO_GATEWAY_MODEL_PATH", str(model_path))
    monkeypatch.delenv("YOLO_GATEWAY_API_KEY", raising=False)

    exit_code = smoke.main([str(image_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "YOLO_GATEWAY_API_KEY" in captured.err


def test_build_smoke_request_contains_exactly_one_image() -> None:
    payload = smoke.build_smoke_request("data:image/png;base64,abc123")
    content = payload["messages"][0]["content"]

    assert payload["model"] == "yolo-cpu-detector"
    assert len(content) == 2
    assert sum(1 for item in content if item["type"] == "image_url") == 1
    assert content[1]["image_url"]["url"] == "data:image/png;base64,abc123"


def test_parse_smoke_completion_parses_json_string_content() -> None:
    completion = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=(
                        '{"detections":[{"label":"person","class_id":0,"confidence":0.91,'
                        '"box":{"x1":1.0,"y1":2.0,"x2":3.0,"y2":4.0}}],'
                        '"image":{"width":640,"height":480,"mime_type":"image/jpeg","byte_length":123},'
                        '"runtime":{"backend":"ultralytics","device":"cpu"}}'
                    )
                )
            )
        ]
    )

    payload = smoke.parse_smoke_completion(completion)

    assert payload["detections"][0]["label"] == "person"
    assert payload["image"]["width"] == 640
    assert payload["runtime"]["device"] == "cpu"


def test_parse_smoke_completion_rejects_unexpected_shape() -> None:
    completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))])

    with pytest.raises(ValueError, match="Unexpected completion response shape"):
        smoke.parse_smoke_completion(completion)


def test_parse_smoke_completion_rejects_invalid_json() -> None:
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="not-json"))]
    )

    with pytest.raises(ValueError, match="invalid JSON in choices\\[0\\]\\.message\\.content"):
        smoke.parse_smoke_completion(completion)


def test_validate_smoke_payload_requires_cpu_runtime() -> None:
    payload = {
        "detections": [],
        "image": {"width": 2, "height": 2},
        "runtime": {"backend": "ultralytics", "device": "cuda"},
    }

    with pytest.raises(ValueError, match="CPU mode is required"):
        smoke.validate_smoke_payload(payload)


def test_request_smoke_completion_reports_gateway_connection_failure() -> None:
    class APIConnectionError(RuntimeError):
        pass

    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(*args, **kwargs):
                    raise APIConnectionError("Connection refused")

    with pytest.raises(RuntimeError, match="Unable to reach local gateway"):
        smoke.request_smoke_completion(
            FakeClient(),
            base_url="http://127.0.0.1:8000/v1",
            model_id="yolo-cpu-detector",
            messages=[],
        )


def test_format_smoke_report_includes_core_fields(tmp_path) -> None:
    model_path = tmp_path / "model.pt"
    report = smoke.format_smoke_report(
        {
            "detections": [],
            "image": {
                "width": 640,
                "height": 480,
                "mime_type": "image/jpeg",
                "byte_length": 123,
            },
            "runtime": {"backend": "ultralytics", "device": "cpu"},
        },
        model_id="yolo-cpu-detector",
        base_url="http://127.0.0.1:8000/v1",
        model_path=model_path,
    )

    assert "Model ID: yolo-cpu-detector" in report
    assert f"Model path: {model_path}" in report
    assert "Base URL: http://127.0.0.1:8000/v1" in report
    assert "Image: 640x480 (image/jpeg, 123 bytes)" in report
    assert "Runtime: ultralytics / cpu" in report
    assert "Detections: 0" in report
