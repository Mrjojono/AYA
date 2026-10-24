"""Open Food Facts local copy adapter."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.barcode.schemas import SourceResult
from aya_api.models import Product


class OffLocalAdapter:
    name = "off_local"
    license = "ODbL"
    enabled = True

    def __init__(self, session: AsyncSession):
        self.session = session

    async def lookup(self, gtin: str) -> SourceResult | None:
        stmt = select(Product).where(Product.barcode == gtin)
        result = await self.session.execute(stmt)
        prod = result.scalars().first()
        if not prod:
            return None
        if prod.source == "openfoodfacts" or prod.license == "ODbL":
            return SourceResult(
                gtin=prod.barcode,
                found=True,
                name=prod.product_name,
                brand=prod.brands,
                category=prod.categories,
                countries=prod.countries,
                ingredients_text=prod.ingredients_text,
                nutrients=prod.nutrients or {},
                image_url=prod.image_url,
                nutriscore_grade=prod.nutriscore_grade,
                nova_group=prod.nova_group,
                source="off_local",
                license="ODbL",
                confidence=prod.confidence or 0.7,
                data_quality=prod.data_quality,
            )
        # also allow if from off but marked differently
        if prod.source and "off" in prod.source:
            return SourceResult(
                gtin=prod.barcode,
                found=True,
                name=prod.product_name,
                brand=prod.brands,
                category=prod.categories,
                countries=prod.countries,
                ingredients_text=prod.ingredients_text,
                nutrients=prod.nutrients or {},
                image_url=prod.image_url,
                nutriscore_grade=prod.nutriscore_grade,
                nova_group=prod.nova_group,
                source="off_local",
                license="ODbL",
                confidence=prod.confidence or 0.7,
                data_quality=prod.data_quality,
            )
        return None

    async def search(self, name: str) -> list[SourceResult]:
        stmt = select(Product).where(Product.product_name.ilike(f"%{name}%")).limit(10)
        result = await self.session.execute(stmt)
        prods = result.scalars().all()
        out = []
        for prod in prods:
            if prod.source == "openfoodfacts" or (prod.source and "off" in prod.source) or prod.license == "ODbL":
                out.append(
                    SourceResult(
                        gtin=prod.barcode,
                        found=True,
                        name=prod.product_name,
                        brand=prod.brands,
                        category=prod.categories,
                        countries=prod.countries,
                        ingredients_text=prod.ingredients_text,
                        nutrients=prod.nutrients or {},
                        image_url=prod.image_url,
                        nutriscore_grade=prod.nutriscore_grade,
                        nova_group=prod.nova_group,
                        source="off_local",
                        license="ODbL",
                        confidence=prod.confidence or 0.7,
                        data_quality=prod.data_quality,
                    )
                )
        return out
