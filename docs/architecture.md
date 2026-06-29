# Architecture

## Product shape

This repository implements a local OpenAI-compatible API-style gateway for CPU-only YOLO single-image object detection.
The Ultralytics backend is implemented, but default tests still mock detector behavior so CI does not require model weights.

The system is intentionally small:

```text
OpenAI-style client
    -> Authorization: Bearer <fixed key>
    -> POST /v1/chat/completions
    -> one base64 image data URL
    -> FastAPI request validation
    -> CPU YOLO detector
    -> OpenAI-like chat completion response containing detection JSON
```

## Architectural priorities

| Priority | Explanation |
|---|---|
| CPU-first | Must run on GPU-less machines. |
| Small API surface | Only implement endpoints needed for compatibility and operation. |
| Fail closed | Reject unsupported inputs before detector execution. |
| No persistence | Images are processed in memory only in the MVP. |
| No background work | Every request is synchronous: one request, one image, one response. |
| Testability | API behavior must be testable with a mocked detector. |
| Honest compatibility | OpenAI-like where useful, but limitations must be clear. |

## Runtime components

| Component | Responsibility |
|---|---|
| FastAPI app | HTTP server and route registration. |
| Auth module | Fixed bearer key validation. |
| OpenAI compatibility schemas | Request/response models and error shapes. |
| Image input parser | Extract one base64 data URL and decode image. |
| Detector interface | Abstract object detection result from YOLO implementation. |
| YOLO implementation | CPU object detection. |
| Configuration | Env-driven model path, CPU device, thresholds, and image size. |
| Tests | Validate auth, endpoint contract, image parsing, and response mapping. |

## Source layout

```text
src/yolo_image_gateway/
  main.py
  config.py
  auth.py
  api/
  vision/
  openai_compat/
```

## Data flow

1. Client sends `POST /v1/chat/completions`.
2. Server validates bearer key.
3. Server validates model ID.
4. Server scans messages for exactly one `image_url` item.
5. Server rejects non-data URLs.
6. Server decodes and validates base64 image.
7. Server runs object detection on CPU with an Ultralytics YOLO backend.
8. Server serializes detections to JSON.
9. Server places JSON as a string inside `choices[0].message.content`.

## Deliberately excluded architecture

The MVP must not include:

- database
- queue
- worker process
- object storage
- remote URL fetcher
- video pipeline
- tracking state
- segmentation output
- user accounts
- provider forwarding
