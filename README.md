# AYA Backend

FastAPI backend for AYA, a nutrition and medication interaction assistant.

## Quick start

```bash
make install
docker compose up -d
make upgrade
make run
```

API docs (Swagger): http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

## Documentation

- [API Overview](docs/api-overview.md) - Endpoints, authentication, workflows
- [Barcode Orchestrator](docs/barcode-orchestrator.md) - Multi-source barcode lookup with coverage matrix
- [OCR Label Extraction](docs/ocr-label-extraction.md) - Label scanning pipeline
- [Privacy Policy](docs/privacy-policy.md) - Privacy information

## Commands

- `make ci` — format, lint, typecheck, tests
- `make run` — dev server
- `make upgrade` / `make downgrade` — DB migrations
- `make import-ddinter` / `make import-wafct` / `make import-oms` / `make import-off` / `make import-lnme` — data imports

## Data sources

- DDInter (drug-drug interactions), WAFCT 2019 (food composition), WHO/FAO 2004 (nutrition thresholds), Open Food Facts, LNME Bénin/Haiti (demo), openFDA.

## Privacy

See `docs/privacy-policy.md`.
