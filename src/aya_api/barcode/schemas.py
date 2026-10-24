"""Common schemas for barcode sources."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

LicenseType = Literal["ODbL", "commercial", "internal", "unknown"]
SourceType = Literal[
    "cache",
    "interne_valide",
    "off_local",
    "gs1_gepir",
    "api_commerciale",
    "photo_fallback",
]


class SourceResult(BaseModel):
    """Normalized result from any barcode source."""

    model_config = ConfigDict(frozen=True)

    gtin: str
    found: bool
    name: str | None = None
    brand: str | None = None
    category: str | None = None
    countries: str | None = None
    ingredients_text: str | None = None
    nutrients: dict | None = None
    image_url: str | None = None
    nutriscore_grade: str | None = None
    nova_group: int | None = None
    source: SourceType
    license: LicenseType
    confidence: float = 0.0
    data_quality: str | None = None
    raw: dict | None = None
