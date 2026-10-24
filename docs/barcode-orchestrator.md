# Orchestrateur de codes-barres (multi-sources)

Ce module permet d'interroger plusieurs sources de produits (codes-barres/EAN) dans un ordre configurable, avec traçabilité complète pour mesurer la couverture par source.

## Architecture

```
src/aya_api/barcode/
├── schemas.py      # Format commun SourceResult
├── base.py         # Interface BarcodeSource (Protocol)
├── config.py       # Chargement sources.yaml
├── registry.py     # Enregistrement des adaptateurs
├── orchestrator.py # Parcours ordonné + traçabilité
└── adapters/
    ├── cache.py        # Table Product déjà consultée
    ├── internal.py     # Produits validés (source/internal ou validé)
    ├── off_local.py    # Copie locale Open Food Facts (ODbL)
    ├── gs1_gepir.py    # Stub GS1 GEPIR
    └── commercial.py   # API commerciale (désactivé par défaut)
```

## Configuration

Fichier `sources.yaml` à la racine :

```yaml
barcode:
  order:
    - cache
    - interne_valide
    - off_local
    - gs1_gepir
    - api_commerciale
  stop_on_first_valid: true
  timeout_per_source_s: 3

search:
  order:
    - interne_valide
    - off_local
    - api_commerciale
  parallel_for_search: true
```

L'adaptateur `api_commerciale` est désactivé par défaut (`AYA_BARCODE_COMMERCIAL_ENABLED=false`). Il ne doit être activé qu'après vérification des CGU/licences et du budget.

## Ordre de résolution

1. **cache** - Déjà vu/consulté dans la base locale
2. **interne_valide** - Produits validés par un relecteur (priorité interne)
3. **off_local** - Copie locale Open Food Facts (licence ODbL)
4. **gs1_gepir** - Information sur le préfixe GS1 (stub)
5. **api_commerciale** - API commerciale (désactivé par défaut)

L'orchestrateur s'arrête au **premier résultat valide** (configurable). Chaque tentative est tracée dans `barcode_lookup_attempt`.

## Traçabilité & Matrice de couverture

Modèle `BarcodeLookupAttempt` enregistre pour chaque source testée :
- `gtin` - Code-barres normalisé
- `source` - Nom de la source testée
- `found` - true/false
- `latency_ms` - Temps de réponse
- `error` - Erreur éventuelle
- `license` - Licence associée
- `chosen` - true si cette source a fourni le résultat retenu
- `confidence` - Score de confiance

La matrice se remplit **automatiquement** à chaque appel à l'orchestrateur. Pas besoin d'importer des produits pour commencer à mesurer.

## Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/products/barcode/{ean}` | GET | Résolution via orchestrateur (fallback direct si non trouvé) |
| `/products/barcode/{ean}/resolve` | GET | Résolution avec trace complète `attempts[]` |
| `/products/lookup` | POST | Lookup par code-barres |
| `/products/coverage/run` | POST | Tester une liste de GTINs en une fois (remplit la matrice) |
| `/products/coverage/matrix` | GET | Matrice GTIN x source (générée depuis `barcode_lookup_attempt`) |
| `/products/coverage/stats` | GET | Stats par source (tentatives, trouvés, erreurs, choisis) |
| `/products/cache/stats` | GET | Stats du cache local |

## Bonnes pratiques

- **Licences séparées**: Les données ODbL restent dans leur schéma. Ne jamais copier aveuglément des données commerciales dans la base ODbL/interne sans vérifier les conditions.
- **Traçabilité**: Toujours garder la provenance (`source`, `license`) par résultat.
- **Mesurer avant d'acheter**: Utiliser la matrice pour décider s'il faut activer une API commerciale en fonction de la couverture réelle sur le marché togolais.
- **Normalisation GTIN**: Les codes sont normalisés (trim, suppression tirets/espaces).
