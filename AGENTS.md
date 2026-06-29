# AGENTS.md — Project Constitution

## 0. Authority and purpose

This file is the governing instruction set for AI coding agents working in this repository.

The repository implements a CPU-first, OpenAI-compatible local API gateway for **single-image YOLO object detection**. It does not implement general chat, object tracking, video processing, segmentation, background jobs, a database, or forwarding to OpenAI.

Agents must follow this constitution before making code changes. If a task prompt conflicts with this file, report the conflict and stop unless the human explicitly updates this constitution.

`AGENTS.md` and `CLAUDE.md` must remain semantically equivalent. If one is changed, update the other in the same change.

---

## 1. Product mission

Build a local HTTP service that allows users to call a YOLO object detector through an OpenAI-compatible API style:

- `Authorization: Bearer <fixed-key>`
- `/v1/chat/completions` as the primary inference endpoint
- `/v1/models` as the model discovery endpoint
- image input attached in the OpenAI-style message content as a base64 data URL
- result returned as an OpenAI-like chat completion response whose assistant message contains a JSON string with detections

The first release target is a simple, auditable, CPU-only service suitable for GPU-less machines.

---

## 2. Product scope

### 2.1 In scope

The MVP must support:

- CPU-only inference.
- One fixed API key loaded from environment/config.
- `GET /healthz`.
- `GET /v1/models`.
- `POST /v1/chat/completions`.
- Exactly one image per request.
- Image supplied as an OpenAI-style `image_url.url` data URL:
  - `data:image/jpeg;base64,...`
  - `data:image/png;base64,...`
  - `data:image/webp;base64,...`
- Object detection only:
  - class ID
  - class label
  - confidence
  - bounding box
  - image width and height
- OpenAI-shaped error responses where practical.
- Tests that do not require GPU.
- Documentation that clearly states compatibility limits.

### 2.2 Explicit non-goals

Do not implement any of the following unless the human updates this constitution:

- Object tracking.
- Video input or video output.
- Segmentation masks.
- Pose estimation.
- Background jobs.
- Queues, workers, Redis, Celery, RQ, schedulers, or job status endpoints.
- Database.
- User management.
- API key creation, rotation, or multi-key accounting.
- Persistent image storage.
- External image fetching from HTTP/HTTPS URLs.
- File upload endpoints.
- OpenAI request forwarding.
- Full OpenAI API compatibility.
- Streaming responses.
- The Responses API as part of the MVP.
- Web UI.
- Training or fine-tuning.
- GPU/CUDA requirement.

---

## 3. Compatibility contract

### 3.1 OpenAI-compatible means

For this project, OpenAI-compatible means:

- The API is served under `/v1`.
- Clients authenticate with `Authorization: Bearer <api_key>`.
- The main request shape follows Chat Completions style:
  - `POST /v1/chat/completions`
  - body contains `model` and `messages`
  - image is attached in message content using `type: "image_url"`
  - base64 image is encoded in `image_url.url` as a data URL
- The model list endpoint responds on `/v1/models`.
- Responses use OpenAI-like top-level fields:
  - `id`
  - `object`
  - `created`
  - `model`
  - `choices`
- Errors use a stable JSON error object.

### 3.2 OpenAI-compatible does not mean

Do not claim or implement:

- All OpenAI model behavior.
- Free-form conversation.
- Text generation.
- Provider forwarding.
- Tool calls.
- Streaming events.
- Stored chat completions.
- Retrieval/list/update/delete chat completion endpoints.
- Multiple image support in the MVP.
- Support for remote image URLs.
- Support for OpenAI organization/project headers beyond ignoring them safely.

### 3.3 Required endpoints

| Endpoint | Required | Notes |
|---|---:|---|
| `GET /healthz` | Yes | Operational health check, outside `/v1`. |
| `GET /v1/models` | Yes | Returns one local model entry. |
| `POST /v1/chat/completions` | Yes | Main image detection endpoint. |

### 3.4 Not implemented endpoints

Return a clear `404` or documented unsupported response for everything else. Do not add endpoints casually.

---

## 4. Request contract

The supported request shape is:

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

### 4.1 Required validation

The server must reject:

- missing `Authorization` header
- invalid bearer token
- missing request body
- missing `model`
- unsupported model
- missing `messages`
- no image content
- more than one image content item
- image content not using `type: "image_url"`
- missing `image_url.url`
- URL that is not a base64 data URL
- `http://`, `https://`, `file://`, or other non-data schemes
- unsupported MIME type
- invalid base64
- decoded image too large
- decoded image that cannot be parsed as an image
- user text that requests tracking, segmentation, video, or background processing

### 4.2 Model name

The first model ID is:

```text
yolo-cpu-detector
```

Do not rename this model ID without updating docs and tests.

---

## 5. Response contract

The assistant message `content` should be a JSON string for client compatibility.

Example assistant content after JSON decoding:

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

The full response should look like an OpenAI chat completion:

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

Do not return raw Python objects or non-JSON-serializable values.

---

## 6. Architecture

### 6.1 Expected package structure

Use the planned package layout unless there is a clear reason to change it:

```text
src/yolo_image_gateway/
  __init__.py
  main.py
  config.py
  auth.py
  api/
    __init__.py
    health.py
    models.py
    chat_completions.py
  vision/
    __init__.py
    detector.py
    image_input.py
    schemas.py
  openai_compat/
    __init__.py
    schemas.py
    errors.py
```

### 6.2 Component responsibilities

| Component | Responsibility |
|---|---|
| `main.py` | FastAPI app creation and router registration. |
| `config.py` | Environment-driven settings. |
| `auth.py` | Bearer API key validation. |
| `api/health.py` | `/healthz`. |
| `api/models.py` | `/v1/models`. |
| `api/chat_completions.py` | Request validation and response mapping. |
| `vision/image_input.py` | Data URL parsing, validation, image decoding. |
| `vision/detector.py` | Detector abstraction and YOLO implementation. |
| `vision/schemas.py` | Detection result schemas. |
| `openai_compat/schemas.py` | OpenAI-shaped request/response schemas. |
| `openai_compat/errors.py` | OpenAI-like error helpers. |

### 6.3 Technology choices

Initial implementation should use:

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Pillow and/or OpenCV for image decoding
- Ultralytics YOLO for first detector implementation
- pytest for tests
- ruff for linting

Future optimization may add:

- ONNX Runtime CPU
- OpenVINO for Intel-oriented CPU optimization

Do not add ONNX Runtime or OpenVINO in the first implementation slice unless the human explicitly asks.

---

## 7. Configuration

Configuration must be environment-based.

Required environment variables:

| Variable | Required | Purpose |
|---|---:|---|
| `YOLO_GATEWAY_API_KEY` | Yes | Fixed bearer API key. |
| `YOLO_GATEWAY_MODEL_ID` | No | Defaults to `yolo-cpu-detector`. |
| `YOLO_GATEWAY_MODEL_PATH` | No | Path to the YOLO weights file used by the Ultralytics backend. |
| `YOLO_GATEWAY_YOLO_MODEL` | No | Legacy alias for `YOLO_GATEWAY_MODEL_PATH`. |
| `YOLO_GATEWAY_DEVICE` | No | Must remain `cpu` in v1. |
| `YOLO_GATEWAY_CONFIDENCE_THRESHOLD` | No | Detection confidence threshold. |
| `YOLO_GATEWAY_IOU_THRESHOLD` | No | YOLO IoU threshold. |
| `YOLO_GATEWAY_IMAGE_SIZE` | No | Inference image size in pixels. |
| `YOLO_GATEWAY_MAX_IMAGE_BYTES` | No | Maximum decoded image size. |

Never hardcode real secrets. `.env` is ignored and `.env.example` may contain fake placeholders only. Model weights are not committed to the repository.

---

## 8. Security rules

- Treat the fixed API key as a secret.
- Never commit real API keys.
- Never log the full API key.
- Never log raw base64 image bodies by default.
- Do not persist uploaded images unless the human changes the scope.
- Do not fetch external URLs.
- Do not accept `file://` inputs.
- Reject invalid inputs before detector execution.
- Fail closed on unsupported models, unsupported MIME types, and unsupported task requests.
- Keep `/healthz` unauthenticated only if it returns no sensitive information.
- Keep `/v1/models` protected by the same bearer auth unless the human explicitly approves unauthenticated model listing.
- Use constant-time comparison for API key validation where practical.

---

## 9. Testing requirements

### 9.1 Tests required for MVP

The first implementation must include tests for:

- `/healthz` returns OK.
- missing API key returns 401.
- malformed auth header returns 401.
- wrong API key returns 401.
- correct API key can access protected endpoints.
- `/v1/models` returns `yolo-cpu-detector`.
- `/v1/chat/completions` rejects missing image.
- `/v1/chat/completions` rejects multiple images.
- `/v1/chat/completions` rejects HTTP/HTTPS image URLs.
- `/v1/chat/completions` rejects invalid base64.
- `/v1/chat/completions` rejects unsupported MIME types.
- valid base64 image reaches a mocked detector.
- mocked detector output is returned as a JSON string inside `message.content`.
- no GPU is required for tests.

### 9.2 Test discipline

- Do not skip tests and claim they passed.
- If tests are blocked by environment, report them as blocked.
- Use mocked detector tests for API behavior.
- Keep at least one tiny valid image fixture for input parsing tests.
- Do not require a large model download for normal unit tests.

---

## 10. Documentation requirements

Update documentation whenever behavior changes.

Required docs:

- `README.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/openai-compatibility.md`
- `docs/security.md`
- `docs/testing-strategy.md`
- `docs/non-goals.md`
- `docs/work-orders/001-api-skeleton.md`

Documentation must not claim:

- production readiness
- full OpenAI compatibility
- real-time performance
- tracking support
- segmentation support
- video support
- GPU acceleration

unless those claims are implemented, tested, and approved.

---

## 11. Workflow rules

For normal implementation after repository initialization:

- Create a branch from current `main`.
- Keep work PR-sized.
- Commit only related files.
- Do not push directly to protected branches.
- Do not merge your own PR.
- Run relevant tests before final report.
- Report skipped and blocked tests honestly.
- Include documentation changes with behavior changes.

Repository initialization may be committed directly by the human from this starter package. After that, use PR-sized work.

---

## 12. First implementation order

Do not jump directly into optimization. Recommended sequence:

1. API skeleton, auth, schemas, request/response validation, mocked detector tests.
2. Ultralytics CPU detector integration.
3. CPU benchmark script and documentation.
4. ONNX Runtime CPU backend investigation and optional implementation.
5. OpenVINO optimization investigation and optional implementation.
6. Hardening, error compatibility, packaging, deployment.

---

## 13. Required final report format for agents

Every implementation agent must report:

```markdown
## Summary
- ...

## Files changed
- ...

## Behavior implemented
- ...

## Tests run
- `command`: result

## Tests not run / skipped / blocked
- ...

## Documentation changed
- ...

## Security notes
- ...

## Known limitations
- ...

## Follow-up recommended
- ...
```

Avoid vague claims like "all tests passed" unless the full relevant test suite actually passed.

---

## 14. Review checklist

Before accepting a PR, verify:

- scope matches work order
- no tracking/video/segmentation/background job code introduced
- no real secret committed
- no external URL fetching introduced
- API key auth is enforced on `/v1` endpoints
- data URL parser rejects unsupported inputs
- response content remains OpenAI-like
- tests are meaningful and GPU-free
- docs match actual behavior
- limitations are stated honestly
