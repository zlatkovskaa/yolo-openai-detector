# Non-goals

This document exists to protect the MVP from scope creep. The MVP is CPU-only.

## Not supported in MVP

| Feature | Reason |
|---|---|
| Tracking | Project is single-shot image detection only. |
| Video | Adds processing complexity and background/job pressure. |
| Segmentation | Different output shape and model/task path. |
| Pose estimation | Different task path. |
| Background jobs | MVP must be one request, one response. |
| Queue/workers | Not needed without video/background processing. |
| Database | No persistent state in MVP. |
| Image persistence | Avoid privacy and storage complexity. |
| Remote image URLs | Avoid SSRF, networking, and fetch complexity. |
| File uploads | OpenAI-style base64 data URL only for MVP. |
| Full OpenAI API | Only a small compatibility subset is intended. |
| OpenAI forwarding | This is a local detector gateway, not an LLM proxy. |
| Web UI | API first. |
| Training/fine-tuning | Inference only. |
| GPU requirement | Must run on GPU-less machines. |
| Model weights in repo | Weights are supplied at runtime, not committed. |

## Scope change process

If any non-goal becomes desired:

1. Update this document.
2. Update `AGENTS.md`.
3. Update `CLAUDE.md`.
4. Update `docs/architecture.md`.
5. Add tests and acceptance criteria before implementation.
