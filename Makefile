.PHONY: test lint format docs

test:
	pytest

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

docs:
	zensical build --strict