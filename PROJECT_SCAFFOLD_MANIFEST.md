# Project Scaffold Manifest

This zip contains the initial repository scaffold for `yolo-image-gateway`.

## Top-level files

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.env.example`
- `.gitignore`
- `pyproject.toml`
- `requirements.txt`
- `requirements-dev.txt`
- `Makefile`

## Documentation

- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/openai-compatibility.md`
- `docs/security.md`
- `docs/testing-strategy.md`
- `docs/non-goals.md`
- `docs/implementation-plan.md`
- `docs/review-checklists.md`
- `docs/decision-log.md`
- `docs/work-orders/001-api-skeleton.md`

## Source skeleton

- `src/yolo_image_gateway/`
- `src/yolo_image_gateway/api/`
- `src/yolo_image_gateway/vision/`
- `src/yolo_image_gateway/openai_compat/`

## Empty folders preserved

- `models/`
- `scripts/`
- `docker/`
- `tests/fixtures/`
- `tests/fixtures/images/`


## GitHub repository automation

The scaffold includes a `.github/` directory with:

- `workflows/ci.yml` for lint, format check, and tests on Python 3.11 and 3.12.
- `pull_request_template.md` with scope, non-goal, OpenAI compatibility, test, documentation, and safety checks.
- `ISSUE_TEMPLATE/bug_report.md` and `ISSUE_TEMPLATE/feature_request.md`.
- `dependabot.yml` for Python and GitHub Actions dependency update PRs.
- `CODEOWNERS` placeholder for repository maintainers.

The workflow is intentionally conservative. It must not require GPU/CUDA, external OpenAI calls, tracking, video, segmentation, background jobs, queues, Redis, Celery, or a database.
