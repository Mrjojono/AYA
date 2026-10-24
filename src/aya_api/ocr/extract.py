"""Structured extraction from OCR results."""

import re
from typing import Any

ALLERGEN_KEYWORDS = [
    "arachide", "cacahuète", "noix", "amande", "gluten", "blé", "orge", "seigle",
    "lait", "lactose", "œuf", "oeuf", "soja", "poisson", "crustacé", "mollusque",
    "céleri", "moutarde", "sésame", "sulfite", "fruits à coque"
]


def extract_allergens(words: list[dict]) -> list[dict]:
    """Extract allergens."""
    allergens = []
    text_blob = " ".join([w["text"].lower() for w in words])
    for kw in ALLERGEN_KEYWORDS:
        if kw in text_blob:
            allergens.append({"name": kw, "confidence": 0.5, "status": "found"})
    return allergens


def extract_nutrition(words: list[dict]) -> dict[str, Any]:
    """Extract nutrition values."""
    text_blob = " ".join([w["text"] for w in words])
    results = {}

    # Look for patterns like "sel 1.2 g", "sucres 8 g"
    patterns = {
        "sel": r"sel[^\d]*(\d+[.,]?\d*)\s*(g|mg)",
        "sodium": r"sodium[^\d]*(\d+[.,]?\d*)\s*(g|mg)",
        "sucres": r"sucres?[^\d]*(\d+[.,]?\d*)\s*(g|mg)",
        "glucides": r"glucides[^\d]*(\d+[.,]?\d*)\s*(g|mg)",
        "lipides": r"lipides?[^\d]*(\d+[.,]?\d*)\s*(g|mg)",
        "energie": r"(énergie|energie|kcal|kj)[^\d]*(\d+[.,]?\d*)\s*(kcal|kj|g|mg)?",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text_blob, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1).replace(",", "."))
                unit = match.group(2) if len(match.groups()) >= 2 else None
                if not unit and key == "energie" and len(match.groups()) >= 3:
                    unit = match.group(3)
                results[key] = {"value": value, "unit": unit, "confidence": 0.5, "status": "extracted"}
            except Exception:
                results[key] = {"value": None, "unit": None, "confidence": 0.0, "status": "ILLISIBLE"}
        else:
            results[key] = {"value": None, "unit": None, "confidence": 0.0, "status": "ILLISIBLE"}

    return results


def extract_ingredients(words: list[dict]) -> dict[str, Any]:
    """Extract ingredients section."""
    text_blob = " ".join([w["text"] for w in words])
    # Find "ingrédients" keyword
    match = re.search(r"ingr[ée]dients?[\s:]+(.+?)(?:\.|allerg[èe]ne|valeur|$)", text_blob, re.IGNORECASE | re.DOTALL)
    if match:
        ingredients_text = match.group(1).strip()[:500]
        return {"text": ingredients_text, "confidence": 0.5, "status": "extracted"}
    return {"text": None, "confidence": 0.0, "status": "ILLISIBLE"}
