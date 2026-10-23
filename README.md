# AYA API

Backend FastAPI du projet AYA.

## Démarrage

```bash
cp .env.example .env
docker compose up --build
```

L'API est disponible sur `http://localhost:8000`, la vérification de santé sur
`/health` et la documentation OpenAPI sur `/docs`.

## Qualité

```bash
uv sync --all-groups
make ci
```

