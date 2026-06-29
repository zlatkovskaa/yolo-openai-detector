# Implementation Plan

## Phase 0 — Repository initialization

Included in this scaffold:

- `AGENTS.md`
- `CLAUDE.md`
- docs
- config placeholders
- source/test folder structure

## Phase 1 — API skeleton and contract tests

Goal:

- FastAPI app
- `/healthz`
- `/v1/models`
- `/v1/chat/completions`
- fixed bearer auth
- OpenAI-like schemas
- image data URL parser
- mocked detector
- tests

Source work order:

```text
docs/work-orders/001-api-skeleton.md
```

## Phase 2 — YOLO CPU detector integration

Goal:

- Integrate Ultralytics detector behind detector abstraction.
- Force CPU by default.
- Normalize detections to project schema.
- Keep mocked API tests independent from model download.

## Phase 3 — CPU benchmark script

Goal:

- Add script for single-image CPU benchmark.
- Measure latency on local machine.
- Do not claim real-time performance by default.

## Phase 4 — Optimization investigation

Optional later:

- ONNX Runtime CPU backend.
- OpenVINO backend.
- Compare latency and package complexity.

No optimization backend should be added before the MVP API behavior is stable and tested.

## Phase 5 — Release hardening

Goal:

- Review errors.
- Review docs.
- Review security.
- Run full tests.
- Produce release-readiness checklist.
