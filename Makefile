.PHONY: ci format lint test typecheck

ci: format lint typecheck test

format:
	uv run ruff format --check .

lint:
	uv run ruff check .

typecheck:
	uv run basedpyright

test:
	uv run pytest

