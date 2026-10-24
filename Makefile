.PHONY: ci format lint test typecheck install run migrate upgrade downgrade import-ddinter import-wafct import-oms

ci: format lint typecheck test

format:
	uv run ruff format --check .

lint:
	uv run ruff check .

typecheck:
	uv run basedpyright

test:
	uv run pytest

install:
	uv sync --all-groups

run:
	uv run uvicorn aya_api.main:app --reload

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

migrate:
	uv run alembic revision --autogenerate -m "$(m)"

import-ddinter:
	uv run python -m aya_api.importers.cli ddinter

import-wafct:
	uv run python -m aya_api.importers.cli wafct

import-oms:
	uv run python -m aya_api.importers.cli oms
import-off:
	uv run python -m aya_api.importers.cli openfoodfacts

import-lnme:
	uv run python -m aya_api.importers.cli lnme
