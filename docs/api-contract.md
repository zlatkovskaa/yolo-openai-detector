# API Contract

## Base URL

Local default:

```text
http://localhost:8000
```

API compatibility namespace:

```text
/v1
```

## Authentication

Protected endpoints require:

```http
Authorization: Bearer <YOLO_GATEWAY_API_KEY>
```

The fixed key is configured by environment variable.

## Configuration

The gateway is configured entirely through environment variables.

| Variable | Purpose | Default / Notes |
|---|---|---|
| `YOLO_GATEWAY_API_KEY` | Fixed bearer API key. | Required. |
| `YOLO_GATEWAY_MODEL_ID` | Local model identifier exposed by `/v1/models`. | `yolo-cpu-detector` |
| `YOLO_GATEWAY_MODEL_PATH` | Path to the YOLO weights file used by the Ultralytics backend. | `yolov8n.pt` |
| `YOLO_GATEWAY_YOLO_MODEL` | Legacy alias for `YOLO_GATEWAY_MODEL_PATH`. | Accepted for compatibility. |
| `YOLO_GATEWAY_DEVICE` | Runtime device. | `cpu` in v1 only; non-CPU values are rejected. |
| `YOLO_GATEWAY_CONFIDENCE_THRESHOLD` | Minimum confidence for detections. | `0.25` |
| `YOLO_GATEWAY_IOU_THRESHOLD` | IoU threshold used by YOLO post-processing. | `0.45` |
| `YOLO_GATEWAY_IMAGE_SIZE` | Inference image size in pixels. | `640` |
| `YOLO_GATEWAY_MAX_IMAGE_BYTES` | Maximum decoded image size. | `10 MiB` default |

## Endpoints

### `GET /healthz`

Operational health check.

Authentication: not required, unless the implementation owner chooses to require it.

Response:

```json
{
  "status": "ok"
}
```

The endpoint must not reveal secrets, model paths, host information, or detailed environment data.

---

### `GET /v1/models`

Model discovery.

Authentication: required.

Response:

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

The exact `created` value may be a fixed timestamp or service startup timestamp. Keep it stable enough for tests.

---

### `POST /v1/chat/completions`

Single-image object detection endpoint.

Authentication: required.

Request:

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

Supported MIME types:

- `image/jpeg`
- `image/png`
- `image/webp`

Unsupported:

- external URLs
- file IDs
- file upload objects
- multiple images
- video
- segmentation requests
- tracking requests

The v1 implementation is CPU-only. GPU/CUDA devices are not selected automatically and non-CPU `YOLO_GATEWAY_DEVICE` values are rejected during settings validation.

Success response:

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
        "content": "{\"detections\":[{\"label\":\"person\",\"class_id\":0,\"confidence\":0.91,\"box\":{\"x1\":120.0,\"y1\":80.0,\"x2\":340.0,\"y2\":500.0}}],\"image\":{\"width\":640,\"height\":480},\"runtime\":{\"backend\":\"ultralytics\",\"device\":\"cpu\"}}"
      },
      "finish_reason": "stop"
    }
  ]
}
```

## Detection JSON schema inside `message.content`

`message.content` is a string containing JSON.

Decoded content:

```json
{
  "detections": [
    {
      "label": "person",
      "class_id": 0,
      "confidence": 0.91,
      "box": {
        "x1": 120.0,
        "y1": 80.0,
        "x2": 340.0,
        "y2": 500.0
      }
    }
  ],
  "image": {
    "width": 640,
    "height": 480
  },
  "runtime": {
    "backend": "ultralytics",
    "device": "cpu"
  }
}
```

## Error shape

Use a stable OpenAI-like error object where practical:

```json
{
  "error": {
    "message": "Exactly one image data URL is required.",
    "type": "invalid_request_error",
    "param": "messages",
    "code": "invalid_image_count"
  }
}
```

Recommended HTTP status codes:

| Case | Status |
|---|---:|
| Missing/wrong API key | 401 |
| Missing/invalid request fields | 400 |
| Unsupported model | 400 |
| Unsupported endpoint | 404 |
| Internal detector failure | 500 |
| Image too large | 413 |
