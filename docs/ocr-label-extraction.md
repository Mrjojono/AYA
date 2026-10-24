# OCR d'étiquettes (Sprint 14)

## Objectif
Extraire depuis une photo d'étiquette : ingrédients, allergènes, valeurs nutritionnelles (sel, sucres, énergie), en marquant explicitement ce qui est illisible. Aucune photo n'est conservée.

## Architecture

```
src/aya_api/ocr/
├── config.py      # Configuration (seuils, langues, répertoires)
├── preprocess.py  # Prétraitement (gris, contraste, débruitage, seuillage)
├── engine.py      # Interface OCR + TesseractEngine (mots avec confiance)
├── quality.py     # Score qualité global
├── extract.py     # Extraction structurée (ingrédients, allergènes, nutrition)
└── pipeline.py    # Pipeline complet avec suppression fichiers

src/aya_api/routers/ocr.py  # Endpoint upload
```

## Pipeline

1. **Réception** (`POST /ocr/label`) - Validation format/taille, sauvegarde temporaire
2. **Prétraitement** - Niveaux de gris, CLAHE, débruitage, seuillage Otsu
3. **OCR** - Tesseract avec confiance par mot
4. **Score qualité** - Moyenne des confiances (seuil à fixer après tests)
5. **Extraction structurée** - Ingrédients, allergènes (liste majeure), valeurs nutritionnelles
6. **Marquage** - Zones illisibles marquées `[ILLISIBLE]`, jamais de devinette
7. **Suppression** - Fichier original + prétraité supprimés systématiquement (même en cas d'erreur)

## Format de résultat

```json
{
  "processing_id": "...",
  "text_extracted": "...",
  "words": [{"text": "...", "confidence": 0.95, ...}],
  "quality": {"avg_confidence": 0.85, "should_retake": false, "word_count": 150},
  "ingredients": {"text": "...", "confidence": 0.8, "status": "extracted"},
  "allergens": [{"name": "arachide", "confidence": 0.5, "status": "found"}],
  "nutrition": {
    "sel": {"value": 1.2, "unit": "g", "confidence": 0.5, "status": "extracted"},
    "sucres": {"value": 8, "unit": "g", "confidence": 0.5, "status": "extracted"}
  },
  "valeurs_critiques": {...},
  "zones_illisibles": ["nutrition.energie"],
  "status": "done"
}
```

## Tests des 20 étiquettes

Structure dans `tests/etiquettes/`:
- `etiquette_01.jpg` + `etiquette_01.txt` (transcription manuelle exacte, zones illisibles marquées `[ILLISIBLE]`)
- `etiquette_01.verite.json` (valeurs critiques: allergènes, sel_g, sucres_g)

Mesures:
- **Taux de lecture**: % caractères corrects / distance d'édition normalisée
- **Taux de réussite valeurs critiques**: allergènes/sel/sucres corrects vs vérité

Test REC-05: Aucune valeur critique fausse sans être signalée comme illisible.

## Configuration
Variables d'environnement:
- `OCR_MAX_UPLOAD_SIZE_MB` (défaut: 10)
- `OCR_MIN_CONFIDENCE` (défaut: 0.0, à ajuster après tests)
- `OCR_LANGUAGES` (défaut: fra+eng)
- `OCR_TMP_DIR` (défaut: uploads/tmp)
- `TESSERACT_CMD` (si besoin)
EOF
echo "done"
