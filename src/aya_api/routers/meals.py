"""Meal recording and extraction routes."""

from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from rapidfuzz import process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Food, Glossary, Meal

router = APIRouter(prefix="/meals", tags=["meals"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/record")
async def record(text: str, session_id: str = "anonymous", session: SessionDep = None) -> dict[str, object]:
    """Record a free-text meal and extract foods."""
    foods = (await session.execute(select(Food))).scalars().all()
    glossary = (await session.execute(select(Glossary))).scalars().all()
    keys = [f.name for f in foods] + [g.term for g in glossary] + [g.canonical for g in glossary]
    matches = process.extract(text, keys, limit=10, score_cutoff=50)
    extracted = []
    seen = set()
    for name, score, _ in matches:
        if name in seen:
            continue
        seen.add(name)
        food = next((f for f in foods if f.name == name), None)
        if food is not None:
            extracted.append({"name": food.name, "canonical": food.name, "score": score, "in_reference": True})
            continue
        g = next((x for x in glossary if x.term == name or x.canonical == name), None)
        if g is not None:
            extracted.append({"name": name, "canonical": g.canonical, "components": g.components, "score": score, "in_reference": True})
            continue
        extracted.append({"name": name, "canonical": name, "score": score, "in_reference": False})
    meal = Meal(session_id=session_id, raw_text=text, foods=str(extracted))
    session.add(meal)
    await session.commit()
    await session.refresh(meal)
    return {"id": meal.id, "raw_text": text, "extracted": extracted, "created_at": meal.created_at.isoformat() if meal.created_at else None}


@router.get("/history")
async def history(session_id: str = "anonymous", limit: int = 50, session: SessionDep = None) -> list[dict[str, object]]:
    """Retrieve previous meals for a session."""
    stmt = select(Meal).where(Meal.session_id == session_id).order_by(Meal.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    meals = result.scalars().all()
    out = []
    for m in meals:
        out.append({
            "id": m.id,
            "session_id": m.session_id,
            "raw_text": m.raw_text,
            "foods": m.foods,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return out


@router.get("/{meal_id}")
async def get_meal(meal_id: int, session: SessionDep = None) -> dict[str, object]:
    """Get meal details."""
    stmt = select(Meal).where(Meal.id == meal_id)
    result = await session.execute(stmt)
    meal = result.scalars().first()
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal not found")
    return {
        "id": meal.id,
        "session_id": meal.session_id,
        "raw_text": meal.raw_text,
        "foods": meal.foods,
        "created_at": meal.created_at.isoformat() if meal.created_at else None,
    }

