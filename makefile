.PHONY: install install-dev lint format test pre-commit act-x86 act-arm

install:
	pip install .

install-dev:
	pip install .[dev]

lint:
	ruff check .

format:
	black .
	ruff check --fix .

test:
	pytest

pre-commit:
	pre-commit run --all-files

docker-build:
	docker build -t turbo:dev_latest .

act-x86:
	act -j pre-commit

act-arm:
	act -j pre-commit --container-architecture linux/arm64

setup: install-dev
	pre-commit install

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
