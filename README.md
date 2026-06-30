# YOLO Image Gateway

OpenAI-compatible local gateway for single-image YOLO object detection.

This repository is governed by `AGENTS.md` and `CLAUDE.md`. The current implementation is CPU-only and intentionally small.

## What is implemented

- fixed bearer authentication
- `GET /healthz`
- `GET /v1/models`
- `POST /v1/chat/completions`
- OpenAI-style request and response envelopes
- exactly one base64 image data URL per request
- Ultralytics YOLO detector backend on CPU
- config-driven model path, confidence threshold, IoU threshold, image size, and decoded image size limit
- mock-based tests that do not require GPU/CUDA or committed model weights

## What is intentionally not supported

- tracking
- video
- segmentation
- background jobs
- queues or workers
- database
- Redis/Celery
- external image URLs
- image persistence
- OpenAI forwarding
- model weights committed to the repo
- GPU/CUDA requirement

## Configuration

Copy `.env.example` to `.env` for local development.

```bash
cp .env.example .env
```

`.env` is ignored by git. `.env.example` contains placeholders only.

| Variable | Purpose | Example / Default |
|---|---|---|
| `YOLO_GATEWAY_API_KEY` | Fixed bearer API key. | `replace-with-local-development-key` |
| `YOLO_GATEWAY_MODEL_ID` | Local model ID exposed by `/v1/models`. | `yolo-cpu-detector` |
| `YOLO_GATEWAY_MODEL_PATH` | Path to the YOLO weights file used by Ultralytics. | `yolov8n.pt` |
| `YOLO_GATEWAY_YOLO_MODEL` | Legacy alias for `YOLO_GATEWAY_MODEL_PATH`. | Optional |
| `YOLO_GATEWAY_DEVICE` | Runtime device. | `cpu` |
| `YOLO_GATEWAY_CONFIDENCE_THRESHOLD` | Detection confidence threshold. | `0.25` |
| `YOLO_GATEWAY_IOU_THRESHOLD` | Non-maximum suppression IoU threshold. | `0.45` |
| `YOLO_GATEWAY_IMAGE_SIZE` | Inference image size in pixels. | `640` |
| `YOLO_GATEWAY_MAX_IMAGE_BYTES` | Maximum decoded image size. | `10485760` |

`YOLO_GATEWAY_DEVICE` must remain `cpu` for v1. Non-CPU values are rejected during settings validation.

Model weights are not committed to the repository. Provide a local file or compatible Ultralytics download target at runtime.

## Run locally

Start the API server:

```bash
./.venv/bin/python -m uvicorn yolo_image_gateway.main:app --reload --host 0.0.0.0 --port 8000
```

The service listens on `http://localhost:8000` by default.

## Test and lint

Run the checks used by this work order:

```bash
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m ruff format --check .
```

## Client compatibility smoke examples

Use the new examples to call the local gateway the same way an OpenAI-style client would:

- [docs/client-usage.md](docs/client-usage.md)
- `examples/openai_client_single_image.py`
- `examples/curl_single_image.sh`
- `scripts/encode_image_data_url.py`

The example flow is:

1. Encode a local image as a base64 data URL.
2. Send one `POST /v1/chat/completions` request to the local gateway.
3. Parse `choices[0].message.content` as JSON.
4. Print detections and image metadata.

## API Surface

### `GET /healthz`

```json
{"status":"ok"}
```

### `GET /v1/models`

Requires `Authorization: Bearer <YOLO_GATEWAY_API_KEY>`.

```json
{
  "object": "list",
  "data": [
    {
      "id": "yolo-cpu-detector",
      "object": "model",
      "created": 1782720000,
      "owned_by": "local"
    }
  ]
}
```

### `POST /v1/chat/completions`

Request example:

```http
POST /v1/chat/completions
Authorization: Bearer <YOLO_GATEWAY_API_KEY>
Content-Type: application/json
```

```json
{
  "model": "yolo-cpu-detector",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Detect objects in this image."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
          }
        }
      ]
    }
  ]
}
```

Accepted image inputs:

- `data:image/jpeg;base64,...`
- `data:image/png;base64,...`
- `data:image/webp;base64,...`

The assistant message `content` is a JSON string:

```json
{
  "id": "chatcmpl-local-...",
  "object": "chat.completion",
  "created": 1782720000,
  "model": "yolo-cpu-detector",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"detections\":[],\"image\":{\"width\":640,\"height\":480},\"runtime\":{\"backend\":\"ultralytics\",\"device\":\"cpu\"}}"
      },
      "finish_reason": "stop"
    }
  ]
}
```

## Unsupported behavior

- multiple images
- HTTP/HTTPS image URLs
- `file://` image URLs
- invalid base64
- unsupported MIME types
- video
- segmentation
- tracking
- background jobs
- OpenAI forwarding

## Governance

Agents must read:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/architecture.md`
4. `docs/api-contract.md`
5. `docs/work-orders/001-api-skeleton.md`

Do not implement features outside the approved scope.

## License

No license has been selected in this scaffold. Add a license only after the project owner chooses one.
