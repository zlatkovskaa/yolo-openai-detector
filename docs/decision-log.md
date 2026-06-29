# Decision Log

## 0001 — Product shape

Decision: Build an OpenAI-compatible local API gateway for single-image YOLO object detection.

Rejected alternatives:

- full OpenAI API clone
- video/tracking pipeline
- native-only custom detection API

Reason:

The project goal is user-facing compatibility with OpenAI-style clients while keeping the system small and reviewable.

## 0002 — Main endpoint

Decision: Use `POST /v1/chat/completions` as the main inference endpoint.

Reason:

The request can carry text plus an image content item in a familiar OpenAI-style shape.

## 0003 — Image input

Decision: Support only base64 data URLs in MVP.

Reason:

Avoid SSRF, external networking, file upload complexity, and storage scope.

## 0004 — Model discovery endpoint

Decision: Include `GET /v1/models`.

Reason:

OpenAI-compatible tools commonly expect model discovery. The endpoint returns one local model.

## 0005 — Health endpoint

Decision: Include `GET /healthz` outside `/v1`.

Reason:

Operational health check, not part of OpenAI compatibility.

## 0006 — No tracking/video/segmentation

Decision: Explicitly exclude tracking, video, and segmentation.

Reason:

The project is a single-shot image detector. These features would change the architecture and validation burden.

## 0007 — No background jobs

Decision: Exclude background jobs, queues, and workers from MVP.

Reason:

The request is synchronous: one image in, detections out.
