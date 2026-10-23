"""Nutrition routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Food
from aya_api.nutrition import total_nutrients

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/total")
async def total(
    food_names: list[str],
    quantities_g: list[float],
    session: SessionDep,
) -> dict[str, float]:
    """Compute total nutrients for a list of foods and quantities."""
    stmt = select(Food).where(Food.name.in_(food_names))
    foods = (await session.execute(stmt)).scalars().all()
    food_dicts: list[dict[str, object]] = [
        {"name": f.name, "nutrients": f.nutrients} for f in foods
    ]
    return total_nutrients(food_dicts, quantities_g)
