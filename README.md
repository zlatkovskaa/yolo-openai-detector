# YOLO Image Gateway

CPU-first YOLO single-image object detection through an OpenAI-compatible API style.

This repository is a governed CPU-first YOLO object detection gateway. Follow `AGENTS.md` and `CLAUDE.md` when changing behavior.

## Mission

Build a local HTTP gateway that accepts a single base64 image attached in an OpenAI-style `/v1/chat/completions` request, runs YOLO object detection on CPU, and returns detections in an OpenAI-like chat completion response.

## Current status

The API skeleton and CPU YOLO backend are implemented.

What is in place:

- fixed bearer authentication
- `GET /healthz`
- `GET /v1/models`
- `POST /v1/chat/completions`
- OpenAI-shaped request and response schemas
- base64 data URL image parsing
- Ultralytics-backed CPU detector adapter
- mock-based tests that do not require model weights

The service remains intentionally narrow:

- one image per request
- no tracking
- no video
- no segmentation
- no background jobs
- no database
- no OpenAI forwarding

Model weights are not committed to the repository.

## MVP scope

| Capability | Status |
|---|---:|
| CPU-only operation | Required |
| Fixed bearer API key | Required |
| `GET /healthz` | Required |
| `GET /v1/models` | Required |
| `POST /v1/chat/completions` | Required |
| One image per request | Required |
| Base64 data URL image input | Required |
| YOLO object detection | Required |
| Tracking | Not supported |
| Video | Not supported |
| Segmentation | Not supported |
| Background jobs | Not supported |
| Database | Not supported |
| External image URLs | Not supported |
| OpenAI forwarding | Not supported |

## Intended API

### Health

```http
GET /healthz
```

Expected response:

```json
{
  "status": "ok"
}
```

### Models

```http
GET /v1/models
Authorization: Bearer <YOLO_GATEWAY_API_KEY>
```

Expected response shape:

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

### Chat completions detection request

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
            "url": "data:image/jpeg;base64,..."
          }
        }
      ]
    }
  ]
}
```

Expected response shape:

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
        "content": "{\"detections\":[],\"image\":{\"width\":640,\"height\":480}}"
      },
      "finish_reason": "stop"
    }
  ]
}
```

`message.content` is intentionally a JSON string for OpenAI client compatibility.

## Setup expectation

The first implementation should use Python 3.11+.

Planned stack:

- FastAPI
- Pydantic
- Uvicorn
- Pillow and/or OpenCV
- Ultralytics YOLO
- pytest
- ruff

## Environment variables

Copy `.env.example` to `.env` for local development.

```bash
cp .env.example .env
```

Required:

```bash
YOLO_GATEWAY_API_KEY=replace-with-local-development-key
```

Important runtime settings:

- `YOLO_GATEWAY_MODEL_PATH`
- `YOLO_GATEWAY_DEVICE` must remain `cpu` in v1
- `YOLO_GATEWAY_CONFIDENCE_THRESHOLD`
- `YOLO_GATEWAY_IOU_THRESHOLD`
- `YOLO_GATEWAY_IMAGE_SIZE`

`YOLO_GATEWAY_YOLO_MODEL` is retained as a compatibility alias.

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
