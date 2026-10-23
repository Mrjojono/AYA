# AYA Backend

FastAPI backend for AYA, a nutrition and medication interaction assistant.

## Quick start

```bash
cp .env.example .env  # if present
make install
docker compose up -d
make upgrade
make run
```

API docs: http://localhost:8000/docs

## Commands

- `make ci` — format, lint, typecheck, tests
- `make run` — dev server
- `make upgrade` / `make downgrade` — DB migrations
- `make import-ddinter` / `make import-wafct` / `make import-oms` — data imports

## Data sources

- DDInter (drug-drug interactions), WAFCT 2019 (food composition), WHO/FAO 2004 (nutrition thresholds), Open Food Facts, openFDA.

## Privacy

See `docs/privacy-policy.md`.