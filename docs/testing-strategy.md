# Testing Strategy

## Test philosophy

The gateway must be testable without GPU, without large model downloads, and without external network access.

The CPU YOLO backend is implemented, but default tests should still use fakes and mocks so CI does not require committed weights or internet access.

## Default commands

Use these commands for local verification and CI parity:

```bash
./.venv/bin/python -m pytest
./.venv/bin/python -m ruff check .
./.venv/bin/python -m ruff format --check .
```

## Required test groups

| Group | Purpose |
|---|---|
| Auth tests | Verify fixed bearer key enforcement. |
| Model endpoint tests | Verify `/v1/models` shape. |
| Request validation tests | Verify rejected inputs. |
| Image parser tests | Verify data URL parsing and base64 decoding. |
| Chat completion tests | Verify OpenAI-like response shape. |
| Detector adapter tests | Verify detector output normalization. |
| Config tests | Verify CPU-only device handling and default values. |

## Required MVP tests

- `/healthz` returns `{"status": "ok"}`.
- missing API key returns 401.
- malformed auth header returns 401.
- wrong API key returns 401.
- correct API key returns 200.
- `/v1/models` returns `yolo-cpu-detector`.
- no image returns 400.
- multiple images returns 400.
- HTTP image URL returns 400.
- file URL returns 400.
- invalid base64 returns 400.
- unsupported MIME type returns 400.
- oversized decoded image returns 413.
- valid base64 image reaches mocked detector.
- mocked detector output appears as JSON string in `choices[0].message.content`.
- default config resolves to CPU.
- non-CPU device values are rejected at settings validation.
- detector adapter converts Ultralytics result objects into project schemas.
- detector load failures are reported as controlled API errors.
- tests do not require model weights.
- tests do not require GPU/CUDA.

## Test fixtures

Use tiny generated or committed sample images under:

```text
tests/fixtures/images/
```

Keep fixtures small.

Do not require real YOLO model weights for the default test suite.

## Test reporting rule

A skipped test is not a passing test.

Reports must distinguish:

- passed
- failed
- skipped
- not run
- blocked by environment
