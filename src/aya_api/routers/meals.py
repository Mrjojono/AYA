"""Meal recording and extraction routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from rapidfuzz import process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Food, Meal

router = APIRouter(prefix="/meals", tags=["meals"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/record")
async def record(text: str, session: SessionDep) -> dict[str, object]:
    """Record a free-text meal and extract foods."""
    foods = (await session.execute(select(Food))).scalars().all()
    keys = [f.name for f in foods]
    matches = process.extract(text, keys, limit=5, score_cutoff=60)
    extracted = []
    for name, score, _ in matches:
        food = next((f for f in foods if f.name == name), None)
        if food is not None:
            extracted.append({"name": food.name, "score": score})
    meal = Meal(session_id="anonymous", raw_text=text, foods=str(extracted))
    session.add(meal)
    await session.commit()
    return {"raw_text": text, "extracted": extracted}
