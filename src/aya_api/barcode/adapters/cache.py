"""Cache adapter - lookup from local Product table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.barcode.schemas import SourceResult
from aya_api.models import Product


class CacheAdapter:
    name = "cache"
    license = "internal"
    enabled = True

    def __init__(self, session: AsyncSession):
        self.session = session

    async def lookup(self, gtin: str) -> SourceResult | None:
        stmt = select(Product).where(Product.barcode == gtin)
        result = await self.session.execute(stmt)
        prod = result.scalars().first()
        if not prod:
            return None
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
            source="cache",
            license="internal",
            confidence=prod.confidence or 0.8,
            data_quality=prod.data_quality,
        )

    async def search(self, name: str) -> list[SourceResult]:
        stmt = select(Product).where(Product.product_name.ilike(f"%{name}%")).limit(10)
        result = await self.session.execute(stmt)
        prods = result.scalars().all()
        out = []
        for prod in prods:
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
                    source="cache",
                    license="internal",
                    confidence=prod.confidence or 0.8,
                    data_quality=prod.data_quality,
                )
            )
        return out
