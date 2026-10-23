"""Nutrition calculation helpers."""


def total_nutrients(
    foods: list[dict[str, object]], quantities_g: list[float]
) -> dict[str, float]:
    """Sum nutrients across foods scaled by quantity in grams (per 100g basis)."""
    totals: dict[str, float] = {}
    for food, qty in zip(foods, quantities_g, strict=False):
        nutrients = food.get("nutrients", {})
        factor = qty / 100.0
        if isinstance(nutrients, dict):
            for key, value in nutrients.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    totals[key] = totals.get(key, 0.0) + float(value) * factor
    return totals
