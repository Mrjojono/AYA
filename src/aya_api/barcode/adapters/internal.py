"""Internal validated products adapter."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.barcode.schemas import SourceResult
from aya_api.models import Product


class InternalAdapter:
    name = "interne_valide"
    license = "internal"
    enabled = True

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def lookup(self, gtin: str) -> SourceResult | None:
        stmt = select(Product).where(Product.barcode == gtin)
        result = await self.session.execute(stmt)
        prod = result.scalars().first()
        if not prod:
            return None
        if prod.validated or prod.source == "internal":
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
                source="interne_valide",
                license="internal",
                confidence=max(prod.confidence or 0.9, 0.9),
                data_quality="high",
            )
        return None

    async def search(self, name: str) -> list[SourceResult]:
        stmt = (
            select(Product)
            .where(
                Product.product_name.ilike(f"%{name}%"),
                (Product.validated.is_(True) | (Product.source == "internal")),
            )
            .limit(10)
        )
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
                    source="interne_valide",
                    license="internal",
                    confidence=max(prod.confidence or 0.9, 0.9),
                    data_quality="high",
                )
            )
        return out
