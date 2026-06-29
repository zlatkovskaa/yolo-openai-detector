# Security

## Threat model

This MVP protects a local YOLO detection service with one fixed bearer API key.

Primary risks:

- accidental exposure of the fixed API key
- logging raw image payloads
- accepting unexpected external URLs
- filesystem access through `file://` or path-like input
- denial of service through very large base64 images
- misleading OpenAI compatibility claims
- accidental addition of tracking/video/background job scope

## Security requirements

| Requirement | Rule |
|---|---|
| API key | Load from environment only. |
| Key comparison | Use constant-time comparison where practical. |
| Logging | Never log full bearer token or raw base64 request body. |
| Image input | Accept data URLs only. |
| External URLs | Reject HTTP/HTTPS/file URLs. |
| Size limit | Enforce decoded image byte limit. |
| Persistence | Do not store uploaded images in MVP. |
| `/healthz` | Return minimal non-sensitive status only. |
| `/v1/models` | Require bearer auth. |
| Errors | Do not leak stack traces in API responses. |

## Secret handling

Never commit:

- real API keys
- production `.env` files
- private model registry credentials
- cloud credentials
- SSH keys

Allowed:

- `.env.example` with fake placeholder values
- test keys such as `test-key` inside tests only

## Input rejection policy

Reject before detector execution when:

- authorization is invalid
- model is unsupported
- request contains no image
- request contains more than one image
- request contains an external URL
- request contains invalid base64
- decoded image exceeds maximum byte size
- image cannot be decoded
- user requests tracking, segmentation, video, or background processing

## Security review checklist

Before merge:

- `git diff` contains no secrets
- auth tests pass
- invalid image tests pass
- external URL tests pass
- no persistence was added
- no background processing was added
- docs do not overclaim compatibility or readiness
