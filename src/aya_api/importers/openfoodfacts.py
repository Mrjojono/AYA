"""Open Food Facts importer."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from aya_api.models import ImportReport, Product

if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.ext.asyncio import AsyncSession


def compute_confidence(product: dict[str, Any]) -> tuple[float, str]:
    """Compute confidence score and data quality for a product."""
    score = 0.0
    if product.get("product_name"):
        score += 0.2
    if product.get("ingredients_text"):
        score += 0.2
    if product.get("nutriments") and isinstance(product.get("nutriments"), dict):
        score += 0.2
    if product.get("brands"):
        score += 0.1
    if product.get("categories_tags") or product.get("categories"):
        score += 0.1
    if product.get("image_url") or product.get("image_front_url"):
        score += 0.1
    if product.get("code"):
        score += 0.1
    score = min(score, 1.0)
    if score >= 0.8:
        quality = "high"
    elif score >= 0.5:
        quality = "medium"
    else:
        quality = "low"
    return score, quality


async def import_from_jsonl(
    session: AsyncSession, path: Path, source_version: str = "2024"
) -> int:
    """Import products from JSONL file."""
    count = 0
    with path.open() as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            code = data.get("code") or data.get("barcode") or data.get("_id")
            if not code:
                continue
            code = str(code).strip()
            nutri = data.get("nutriments") or {}
            confidence, quality = compute_confidence(data)
            product_name = data.get("product_name") or data.get("product_name_fr")
            ingredients = data.get("ingredients_text") or data.get(
                "ingredients_text_fr"
            )
            brands = data.get("brands")
            categories = data.get("categories") or ", ".join(
                data.get("categories_tags", [])
            )
            stmt = select(Product).where(Product.barcode == code)
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                existing.product_name = product_name
                existing.brands = brands
                existing.ingredients_text = ingredients
                existing.categories = categories
                existing.nutrients = nutri if isinstance(nutri, dict) else {}
                existing.nutriscore_grade = data.get("nutriscore_grade")
                existing.nova_group = data.get("nova_group")
                existing.image_url = data.get("image_url") or data.get(
                    "image_front_url"
                )
                existing.countries = data.get("countries")
                existing.source_version = source_version
                existing.confidence = confidence
                existing.data_quality = quality
            else:
                prod = Product(
                    barcode=code,
                    product_name=product_name,
                    brands=brands,
                    ingredients_text=ingredients,
                    categories=categories,
                    nutrients=nutri if isinstance(nutri, dict) else {},
                    nutriscore_grade=data.get("nutriscore_grade"),
                    nova_group=data.get("nova_group"),
                    image_url=data.get("image_url") or data.get("image_front_url"),
                    countries=data.get("countries"),
                    source="openfoodfacts",
                    source_version=source_version,
                    confidence=confidence,
                    data_quality=quality,
                )
                session.add(prod)
            count += 1
    report = ImportReport(
        source="openfoodfacts",
        source_version=source_version,
        row_count=count,
        distinct_drugs=count,
        severity_counts="{}",
    )
    session.add(report)
    await session.commit()
    return count
