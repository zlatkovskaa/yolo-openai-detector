from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_dockerfile_exists() -> None:
    assert Path("Dockerfile").is_file()


def test_dockerignore_exists() -> None:
    assert Path(".dockerignore").is_file()


def test_dockerfile_uses_python_and_uvicorn_entrypoint() -> None:
    dockerfile = _read("Dockerfile")

    assert dockerfile.startswith("FROM python:")
    assert '"uvicorn"' in dockerfile
    assert "yolo_image_gateway.main:app" in dockerfile
    assert '"--host", "0.0.0.0"' in dockerfile
    assert '"--port", "8000"' in dockerfile
    assert "EXPOSE 8000" in dockerfile


def test_dockerfile_does_not_reference_cuda_or_model_weights() -> None:
    dockerfile = _read("Dockerfile").lower()

    assert "cuda" not in dockerfile
    assert "gpu" not in dockerfile
    assert "nvidia" not in dockerfile
    assert "*.pt" not in dockerfile
    assert "copy" not in dockerfile or "model.pt" not in dockerfile


def test_dockerignore_excludes_local_models_and_env_files() -> None:
    dockerignore = _read(".dockerignore")

    assert ".git" in dockerignore
    assert ".venv" in dockerignore
    assert ".env" in dockerignore
    assert "*.pt" in dockerignore
    assert "*.onnx" in dockerignore
    assert "*.engine" in dockerignore
    assert "*.xml" in dockerignore
    assert "*.bin" in dockerignore


def test_docker_docs_describe_volume_mounting_and_port() -> None:
    docs = _read("docs/docker.md")

    assert "docker build -t yolo-openai-detector:local ." in docs
    assert "-v /path/on/host/models:/models:ro" in docs
    assert "YOLO_GATEWAY_MODEL_PATH=/models/model.pt" in docs
    assert "http://127.0.0.1:8000/healthz" in docs
