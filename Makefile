.PHONY: install install-dev test lint format run

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements-dev.txt

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

run:
	python -m uvicorn yolo_image_gateway.main:app --host 0.0.0.0 --port 8000
