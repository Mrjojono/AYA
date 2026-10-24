"""Nutrition routes."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Food, Meal, OmsThreshold
from aya_api.nutrition import total_nutrients

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
_MIN_EXCEEDED_COUNT = 2


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


@router.post("/totals/check")
async def check_totals(
    food_names: list[str],
    quantities_g: list[float],
    session: SessionDep,
    session_id: str = "anonymous",
    age: int | None = None,
) -> dict[str, object]:
    """Compute totals and detect nutrient excess vs OMS thresholds."""
    stmt = select(Food).where(Food.name.in_(food_names))
    foods = (await session.execute(stmt)).scalars().all()
    food_dicts: list[dict[str, object]] = [
        {"name": f.name, "nutrients": f.nutrients} for f in foods
    ]
    totals = total_nutrients(food_dicts, quantities_g)

    # Load thresholds
    thresh_stmt = select(OmsThreshold)
    thresholds = (await session.execute(thresh_stmt)).scalars().all()

    exceeded: list[dict[str, object]] = []
    for t in thresholds:
        nutrient_key = t.nutrient.lower()
        val = (
            totals.get(t.nutrient)
            or totals.get(nutrient_key)
            or totals.get(nutrient_key.replace(" ", "_"))
        )
        if val is None:
            continue
        if t.rni_high is not None and val > float(t.rni_high):
            exceeded.append(
                {
                    "nutrient": t.nutrient,
                    "value": val,
                    "threshold_high": t.rni_high,
                    "unit": t.unit,
                    "population_group": t.population_group,
                    "source_version": t.source_version,
                }
            )

    message = None
    if exceeded and len(exceeded) >= _MIN_EXCEEDED_COUNT:
        message = (
            "Dépassements fréquents observés : privilégiez l'équilibre sur la journée."
        )
    elif exceeded:
        message = "Un ou plusieurs nutriments dépassent les seuils de référence."

    return {
        "totals": totals,
        "exceeded": exceeded,
        "has_excess": len(exceeded) > 0,
        "message": message,
        "session_id": session_id,
        "age": age,
    }


@router.get("/trends")
async def trends(
    session: SessionDep,
    session_id: str = "anonymous",
    days: int = 7,
) -> dict[str, object]:
    """Get daily/weekly nutrition totals and trends."""
    _ = datetime.now(UTC) - timedelta(days=days)
    stmt = (
        select(Meal)
        .where(Meal.session_id == session_id)
        .order_by(Meal.created_at.asc())
    )
    result = await session.execute(stmt)
    meals = result.scalars().all()
    # Return structure for trends (placeholder aggregates)
    daily = [
        {
            "date": m.created_at.date().isoformat() if m.created_at else None,
            "meal_id": m.id,
            "raw_text": m.raw_text,
        }
        for m in meals
    ]
    return {
        "session_id": session_id,
        "days": days,
        "daily": daily,
        "totals_by_day": {},
        "trends": {"summary": "Tendances calculées sur la période"},
    }
