# Client Usage

This repository ships a local OpenAI-compatible YOLO gateway and a few smoke examples that call it the same way a normal client would.

## Install dependencies

Install the local development dependencies, including the OpenAI Python client used by the example script:

```bash
python -m pip install -e .[dev]
```

If you prefer the repository helper:

```bash
make install-dev
```

## Configure the local gateway

Create `.env` from the example and set your local values:

```bash
cp .env.example .env
```

Recommended environment variables:

- `YOLO_GATEWAY_API_KEY`
- `YOLO_GATEWAY_BASE_URL` for the examples, defaulting to `http://127.0.0.1:8000/v1`
- `YOLO_GATEWAY_MODEL_ID`, defaulting to `yolo-cpu-detector`
- `YOLO_GATEWAY_MODEL_PATH`
- `YOLO_GATEWAY_DEVICE=cpu`
- `YOLO_GATEWAY_CONFIDENCE_THRESHOLD`
- `YOLO_GATEWAY_IOU_THRESHOLD`
- `YOLO_GATEWAY_IMAGE_SIZE`

Model weights are not committed to Git. Point `YOLO_GATEWAY_MODEL_PATH` at a local YOLO weight file or compatible Ultralytics model source.

## Start the server

```bash
./.venv/bin/python -m uvicorn yolo_image_gateway.main:app --host 0.0.0.0 --port 8000
```

The examples assume the gateway is reachable at `http://127.0.0.1:8000/v1`.

## Encode a local image

Use the helper to turn a local image into an OpenAI-style data URL:

```bash
./.venv/bin/python scripts/encode_image_data_url.py path/to/image.png
```

Supported file extensions:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

Unsupported file types are rejected.

## OpenAI Python client example

Call the local gateway with a local `base_url`:

```bash
YOLO_GATEWAY_API_KEY=replace-with-local-development-key \
YOLO_GATEWAY_BASE_URL=http://127.0.0.1:8000/v1 \
YOLO_GATEWAY_MODEL_ID=yolo-cpu-detector \
./.venv/bin/python examples/openai_client_single_image.py path/to/image.png
```

The script:

- encodes the local image as a base64 data URL
- sends one `chat.completions.create(...)` request
- parses `choices[0].message.content` as JSON
- prints a readable detection summary and the raw JSON payload

## Curl example

Use the shell example to post one local image without installing any extra tooling beyond Python and curl:

```bash
YOLO_GATEWAY_API_KEY=replace-with-local-development-key \
YOLO_GATEWAY_BASE_URL=http://127.0.0.1:8000/v1 \
bash examples/curl_single_image.sh path/to/image.png
```

The script accepts PNG, JPEG, and WebP files. It uses the helper encoder script to generate the data URL.

## Expected response shape

The gateway returns an OpenAI-like chat completion object. The assistant message content is a JSON string.

Decoded content shape:

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

## Troubleshooting

| Symptom | Meaning |
|---|---|
| `401 Unauthorized` | `YOLO_GATEWAY_API_KEY` is missing or wrong. |
| Model unavailable | `YOLO_GATEWAY_MODEL_PATH` is missing or invalid, or the model cannot load. |
| HTTP image URL rejected | Remote image URLs are intentionally not supported. |
| Tracking/video/segmentation/background job request rejected | Those request intents are intentionally not supported in v1. |
| Empty or missing detections | The image may not contain objects the detector recognizes, or the confidence threshold may be too high. |
| `model weights not found` | Model weights are not committed to Git and must be provided locally. |
