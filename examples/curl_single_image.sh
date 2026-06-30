#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 path/to/image.(jpg|jpeg|png|webp)" >&2
  exit 64
fi

if [[ -z "${YOLO_GATEWAY_API_KEY:-}" ]]; then
  echo "Error: set YOLO_GATEWAY_API_KEY to your local gateway key." >&2
  exit 1
fi

base_url="${YOLO_GATEWAY_BASE_URL:-http://127.0.0.1:8000/v1}"
model_id="${YOLO_GATEWAY_MODEL_ID:-yolo-cpu-detector}"
image_path="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image_data_url="$(python3 "$repo_root/scripts/encode_image_data_url.py" "$image_path")"

request_body="$(
  python3 - "$model_id" "$image_data_url" <<'PY'
import json
import sys

model_id = sys.argv[1]
image_data_url = sys.argv[2]

payload = {
    "model": model_id,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Detect objects in this image.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url,
                    },
                },
            ],
        }
    ],
}

print(json.dumps(payload))
PY
)"

curl --fail-with-body -sS "${base_url%/}/chat/completions" \
  -H "Authorization: Bearer ${YOLO_GATEWAY_API_KEY}" \
  -H "Content-Type: application/json" \
  --data "$request_body"
