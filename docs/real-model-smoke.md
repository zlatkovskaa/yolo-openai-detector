# Real Model Smoke Validation

This guide shows how to smoke test the local gateway against a real YOLO model file that already exists on your machine.

## What this smoke test proves

- The gateway server can start with a real local model path.
- The local gateway can accept one base64 image data URL.
- The OpenAI-style client path works against the local `base_url`.
- The assistant response is OpenAI-like and `choices[0].message.content` is a JSON string.
- The parsed JSON contains image metadata, runtime metadata, and detections.
- CPU mode is being used by the gateway response.

## What it does not prove

- Detection accuracy on your image set.
- Throughput or performance under load.
- GPU/CUDA behavior.
- Multiple-image handling.
- Video, tracking, segmentation, background jobs, queues, or persistence.
- Any real OpenAI API usage.

## Prerequisites

- Python dependencies are installed locally, including the OpenAI Python client used by the smoke script.
- A local YOLO model file already exists on disk.
- The gateway server is already running locally.
- You have one local image file to test.

Model weights are not committed to Git. The smoke script does not download weights automatically.

## Provide `YOLO_GATEWAY_MODEL_PATH`

Set `YOLO_GATEWAY_MODEL_PATH` to a real local file:

```bash
export YOLO_GATEWAY_MODEL_PATH=/path/to/model.pt
export YOLO_GATEWAY_API_KEY=local-dev-key
export YOLO_GATEWAY_DEVICE=cpu
```

If the model file is missing or invalid, the smoke script exits before it sends any request.

## Start the gateway locally

Use the FastAPI app entry point:

```bash
YOLO_GATEWAY_MODEL_PATH=/path/to/model.pt \
YOLO_GATEWAY_API_KEY=local-dev-key \
YOLO_GATEWAY_DEVICE=cpu \
./.venv/bin/python -m uvicorn yolo_image_gateway.main:app --host 127.0.0.1 --port 8000
```

The smoke script defaults to `http://127.0.0.1:8000/v1` unless `YOLO_GATEWAY_BASE_URL` is set.

## Run the smoke script

In a second terminal:

```bash
YOLO_GATEWAY_MODEL_PATH=/path/to/model.pt \
YOLO_GATEWAY_API_KEY=local-dev-key \
./.venv/bin/python scripts/smoke_real_model.py path/to/image.jpg
```

Optional overrides:

- `YOLO_GATEWAY_BASE_URL` defaults to `http://127.0.0.1:8000/v1`
- `YOLO_GATEWAY_MODEL_ID` defaults to `yolo-cpu-detector`

## Expected successful output

The script prints:

- model ID
- model path
- base URL
- image metadata
- runtime metadata
- detection count
- top detections, if any
- the raw JSON payload

Example:

```text
Model ID: yolo-cpu-detector
Model path: /path/to/model.pt
Base URL: http://127.0.0.1:8000/v1
Image: 640x480 (image/jpeg, 123456 bytes)
Runtime: ultralytics / cpu
Detections: 2
Top detections:
- person (class 0, confidence 0.912) [120.0, 80.0, 340.0, 500.0]
- bicycle (class 1, confidence 0.801) [40.0, 90.0, 210.0, 320.0]
```

## Common failures

| Symptom | Meaning |
|---|---|
| `YOLO_GATEWAY_MODEL_PATH` is missing | Set the variable to a local model file. |
| `YOLO_GATEWAY_MODEL_PATH does not point to an existing file` | The path is invalid or the file is absent. |
| `YOLO_GATEWAY_API_KEY` is missing | Set the local gateway bearer token. |
| `401 Unauthorized` | The local gateway key is wrong or missing. |
| Server not running / connection refused | Start the gateway first or check `YOLO_GATEWAY_BASE_URL`. |
| Wrong base URL | The client is pointed at the wrong host or port. |
| Unsupported image type | Use `.jpg`, `.jpeg`, `.png`, or `.webp`. |
| Model load failure | The local model path is wrong or the model cannot be loaded by the server. |
| Invalid JSON in `choices[0].message.content` | The gateway response shape is not what the smoke script expects. |
| Runtime device is not `cpu` | The gateway is not running in CPU mode. |

## Safety notes

- Model weights are not committed to Git.
- No OpenAI API calls are made.
- CPU-only is the default and required for v1 smoke validation.
