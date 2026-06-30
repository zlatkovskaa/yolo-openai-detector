# Docker Packaging

This repository includes a minimal CPU-only Docker image so the gateway can be run locally without setting up a full Python environment first.

## What Docker packaging is for

- Building a local container image for the gateway.
- Running the existing FastAPI app in a reproducible CPU-only environment.
- Mounting a local YOLO model file from the host at runtime.

## What it does not include

- Model weights baked into the image.
- Automatic model downloads.
- GPU/CUDA support.
- ONNX or OpenVINO backends.
- OpenAI forwarding.
- Tracking, video, segmentation, background jobs, queues, or persistence.

## Build the image

From the repository root:

```bash
docker build -t yolo-openai-detector:local .
```

The image uses a Python base image and installs the project code into the container.

## Run the container

Mount a local model directory read-only and provide the required environment variables:

```bash
docker run --rm \
  -p 8000:8000 \
  -e YOLO_GATEWAY_API_KEY=local-dev-key \
  -e YOLO_GATEWAY_MODEL_PATH=/models/model.pt \
  -e YOLO_GATEWAY_DEVICE=cpu \
  -v /path/on/host/models:/models:ro \
  yolo-openai-detector:local
```

The gateway listens on `http://127.0.0.1:8000` on the host side.

## Health check

Verify the container is up:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected response:

```json
{"status":"ok"}
```

## Use the existing client examples

Once the container is running, use the same client examples documented in the repository:

- [docs/client-usage.md](client-usage.md)
- `examples/openai_client_single_image.py`
- `examples/curl_single_image.sh`

Point `YOLO_GATEWAY_BASE_URL` at `http://127.0.0.1:8000/v1` when calling the container.

## Common failures

| Symptom | Meaning |
|---|---|
| Model path missing inside container | `YOLO_GATEWAY_MODEL_PATH` points to a path that does not exist in the mounted volume. |
| Wrong host-to-container mount | The host directory was not mounted to the path referenced by `YOLO_GATEWAY_MODEL_PATH`. |
| Missing API key | `YOLO_GATEWAY_API_KEY` was not provided. |
| Port already in use | Host port `8000` is already occupied. |
| Server starts but model fails to load | The mounted model file is invalid or incompatible with the server. |

## Safety notes

- Model weights are not committed to Git.
- Model weights are not baked into the image by default.
- Secrets are not baked into the image.
- No OpenAI API forwarding is used.
- CPU-only is the default and only supported runtime mode for v1.
