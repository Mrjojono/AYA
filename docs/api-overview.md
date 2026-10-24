# AYA API Overview

## Authentication
- `POST /auth/anonymous` - Create anonymous device session
- `POST /auth/refresh` - Refresh tokens
- `GET /auth/me` - Get current session

## Profile & Consent
- `POST /profile` - Create/update profile
- `GET /profile` - Get profile
- `PUT /profile` - Update profile
- `POST /consent` - Set consent by purpose
- `GET /consent` - Get consents
- `GET /referentials/conditions` - List conditions
- `GET /referentials/allergens` - List allergens

## Medications
- `GET /medications/search?q=...` - Fuzzy search
- `GET /medications/related?dci=...&name=...` - Medications with same active substance

## Meals & History
- `POST /meals/record` - Record meal with extraction
- `GET /meals/history` - Meal history
- `GET /meals/{id}` - Meal details
- `GET /glossary/lookup?term=...` - Glossary lookup

## Nutrition
- `POST /nutrition/total` - Compute totals
- `POST /nutrition/totals/check` - Check against OMS thresholds
- `GET /nutrition/trends` - Nutrition trends

## Rules & Engine
- `GET /rules/check?drug=...&food=...` - Check interaction
- `GET /rules/matrix` - Active rules matrix
- `GET /engine/evaluate?drug=...&food=...` - Full evaluation (red/orange/unavailable)

## Orchestration
- `POST /orchestrator/analyze` - Full meal analysis
- `GET /orchestrator/status` - Analysis status

## Products & Barcodes
- `GET /products/barcode/{ean}` - Lookup (orchestrated)
- `GET /products/barcode/{ean}/resolve` - Lookup with full trace
- `POST /products/lookup` - Lookup by barcode
- `POST /products/coverage/run` - Test multiple GTINs
- `GET /products/coverage/matrix` - Coverage matrix (auto-filled)
- `GET /products/coverage/stats` - Coverage statistics
- `GET /products/cache/stats` - Cache statistics

## OCR
- `POST /ocr/label` - Process label image (multipart/form-data)

## System
- `GET /health` - Health check

Interactive docs available at `/docs` (Swagger UI) and `/redoc`.
