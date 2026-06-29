# Work Order 001 — API Skeleton and Contract Tests

## Goal

Create the first working FastAPI service skeleton for a CPU-first YOLO single-image object detection gateway with OpenAI-compatible API style.

This first task should focus on API contract, authentication, validation, schemas, and mocked detector behavior. Do not integrate real YOLO unless all contract work is complete and tests remain independent of GPU/model downloads.

## Governing instructions

Read first:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/api-contract.md`
4. `docs/security.md`
5. `docs/testing-strategy.md`

## Scope

Implement:

- FastAPI app factory or app instance.
- `GET /healthz`.
- `GET /v1/models`.
- `POST /v1/chat/completions`.
- Fixed bearer API key auth from environment.
- Settings module.
- OpenAI-like request/response schemas.
- OpenAI-like error helper.
- Base64 data URL parser.
- Single image extraction from messages.
- Mockable detector interface.
- Tests for auth, validation, model discovery, and response shape.

## Non-goals

Do not implement:

- tracking
- video
- segmentation
- background jobs
- queue/worker infrastructure
- database
- persistent image storage
- external image URL fetching
- OpenAI forwarding
- full OpenAI API compatibility
- streaming
- real model benchmark

## Required behavior

### `/healthz`

- Returns `{"status": "ok"}`.
- Does not reveal secrets or model paths.

### `/v1/models`

- Requires valid bearer key.
- Returns one model ID: `yolo-cpu-detector`.

### `/v1/chat/completions`

- Requires valid bearer key.
- Accepts only model `yolo-cpu-detector`.
- Extracts exactly one image from `messages`.
- Accepts only `data:image/jpeg;base64,...`, `data:image/png;base64,...`, or `data:image/webp;base64,...`.
- Rejects external URLs.
- Rejects multiple images.
- Rejects invalid base64.
- Calls detector interface with decoded image.
- Returns detections in an OpenAI-like response.
- `choices[0].message.content` must be a JSON string, not a raw object.

## Required tests

- `/healthz` returns OK.
- missing API key returns 401.
- malformed auth header returns 401.
- wrong API key returns 401.
- correct API key accesses `/v1/models`.
- `/v1/models` returns `yolo-cpu-detector`.
- no image returns 400.
- multiple images returns 400.
- HTTP image URL returns 400.
- file URL returns 400.
- unsupported MIME type returns 400.
- invalid base64 returns 400.
- valid tiny image reaches mocked detector.
- mocked detector result appears inside JSON string content.

## Implementation guidance

Suggested files:

```text
src/yolo_image_gateway/main.py
src/yolo_image_gateway/config.py
src/yolo_image_gateway/auth.py
src/yolo_image_gateway/api/health.py
src/yolo_image_gateway/api/models.py
src/yolo_image_gateway/api/chat_completions.py
src/yolo_image_gateway/vision/image_input.py
src/yolo_image_gateway/vision/detector.py
src/yolo_image_gateway/vision/schemas.py
src/yolo_image_gateway/openai_compat/schemas.py
src/yolo_image_gateway/openai_compat/errors.py
tests/
```

## Final report required

```markdown
## Summary
- ...

## Files changed
- ...

## Tests run
- `command`: result

## Tests not run / blocked
- ...

## How to run locally
- ...

## Example request
- ...

## Security notes
- ...

## Known limitations
- ...
```
