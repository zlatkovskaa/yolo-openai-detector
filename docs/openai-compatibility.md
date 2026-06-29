# OpenAI Compatibility

## Compatibility goal

The goal is practical compatibility for users who want to point OpenAI-style clients at a local object detection gateway.

This project emulates only a small, documented subset of OpenAI API behavior.

## Supported OpenAI-like behavior

| Feature | Supported |
|---|---:|
| `/v1` path prefix | Yes |
| Bearer API key in `Authorization` header | Yes |
| `GET /v1/models` | Yes |
| `POST /v1/chat/completions` | Yes |
| `model` request field | Yes |
| `messages` request field | Yes |
| image as `content[].type = "image_url"` | Yes |
| base64 data URL image input | Yes |
| OpenAI-like `choices[]` response | Yes |
| assistant message with `role: "assistant"` | Yes |

## Unsupported behavior

| Feature | Supported |
|---|---:|
| Text generation | No |
| Free-form multi-turn chat semantics | No |
| Streaming | No |
| Tool calls | No |
| Function calling | No |
| Response storage | No |
| Chat completion retrieve/update/delete/list | No |
| Multiple image input | No |
| Remote image URLs | No |
| File IDs | No |
| Audio/video | No |
| OpenAI provider forwarding | No |
| Organization/project header handling | No functional behavior |

## Why `GET /v1/models` exists

Some OpenAI-compatible clients and tools call the model list endpoint to discover available model IDs. The gateway exposes one local model:

```text
yolo-cpu-detector
```

## Why `message.content` is a JSON string

OpenAI chat completion messages conventionally carry content as text/string-like content. For compatibility, this gateway returns detection results as a JSON-encoded string inside `choices[0].message.content`, rather than returning a raw object.

Clients should parse it:

```python
import json

payload = json.loads(response.choices[0].message.content)
detections = payload["detections"]
```

## Compatibility references

The project design follows the public OpenAI API patterns for:

- bearer authentication
- `/v1/chat/completions`
- `/v1/models`
- base64 data URL image input in image-capable chat requests

See the official OpenAI API documentation for current upstream API behavior.
