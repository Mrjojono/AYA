"""OCR pipeline."""

import os
import uuid
from pathlib import Path

from aya_api.ocr.config import ocr_config
from aya_api.ocr.engine import get_engine
from aya_api.ocr.extract import extract_allergens, extract_ingredients, extract_nutrition
from aya_api.ocr.preprocess import preprocess_image
from aya_api.ocr.quality import compute_quality


class OCRPipeline:
    """Main OCR pipeline."""

    def __init__(self):
        self.engine = get_engine()

    async def process(self, image_path: Path) -> dict:
        """Process image through full pipeline."""
        preprocessed = None
        try:
            # Preprocess
            preprocessed = preprocess_image(image_path)

            # OCR
            words = self.engine.read_text(preprocessed)

            # Quality
            quality = compute_quality(words)

            # Extract
            ingredients = extract_ingredients(words)
            allergens = extract_allergens(words)
            nutrition = extract_nutrition(words)

            # Build result
            full_text = " ".join([w["text"] for w in words])
            zones_illisibles = []
            for key, val in nutrition.items():
                if val.get("status") == "ILLISIBLE":
                    zones_illisibles.append(f"nutrition.{key}")
            if ingredients.get("status") == "ILLISIBLE":
                zones_illisibles.append("ingredients")
            if not allergens:
                zones_illisibles.append("allergens.possibly_absent_or_unreadable")

            result = {
                "text_extracted": full_text,
                "words": words,
                "quality": quality,
                "ingredients": ingredients,
                "allergens": allergens,
                "nutrition": nutrition,
                "valeurs_critiques": {
                    "allergenes": allergens,
                    "sel": nutrition.get("sel"),
                    "sucres": nutrition.get("sucres"),
                    "sodium": nutrition.get("sodium"),
                },
                "zones_illisibles": zones_illisibles,
                "status": "done",
            }
            return result
        finally:
            # Always delete files after processing
            try:
                if image_path.exists():
                    os.unlink(image_path)
            except Exception:
                pass
            try:
                if preprocessed and preprocessed.exists() and preprocessed != image_path:
                    os.unlink(preprocessed)
            except Exception:
                pass
