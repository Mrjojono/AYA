"""Orchestration routes for full meal analysis."""

from typing import Annotated

from fastapi import APIRouter, Depends
from rapidfuzz import process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Food, Glossary, Meal
from aya_api.nutrition import total_nutrients
from aya_api.rules import check

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/analyze")
async def analyze_meal(
    text: str,
    session: SessionDep,
    session_id: str = "anonymous",
    food_names: list[str] | None = None,
    quantities_g: list[float] | None = None,
    medications: list[str] | None = None,
) -> dict[str, object]:
    """Orchestrate full analysis: extract, compute nutrition, check interactions."""
    foods_db = (await session.execute(select(Food))).scalars().all()
    glossary = (await session.execute(select(Glossary))).scalars().all()

    extracted = []
    if food_names:
        for name in food_names:
            f = next((x for x in foods_db if x.name.lower() == name.lower()), None)
            if f:
                extracted.append({"name": f.name, "in_reference": True})
            else:
                extracted.append({"name": name, "in_reference": False})
    else:
        # simple extraction from text
        keys = (
            [f.name for f in foods_db]
            + [g.term for g in glossary]
            + [g.canonical for g in glossary]
        )
        matches = process.extract(text, keys, limit=8, score_cutoff=50)
        seen = set()
        for name, score, _ in matches:
            if name in seen:
                continue
            seen.add(name)
            extracted.append({"name": name, "score": score, "in_reference": True})

    # Nutrition
    totals: dict = {}
    if food_names and quantities_g:
        food_dicts = [
            {"name": f.name, "nutrients": f.nutrients}
            for f in foods_db
            if f.name in food_names
        ]
        totals = total_nutrients(food_dicts, quantities_g)

    # Interactions
    interactions = []
    meds = medications or []
    for med in meds:
        for ex in extracted:
            sev = await check(session, med, ex["name"])
            if sev:
                interactions.append({"drug": med, "food": ex["name"], "severity": sev})

    meal = Meal(session_id=session_id, raw_text=text, foods=str(extracted))
    session.add(meal)
    await session.commit()
    await session.refresh(meal)

    return {
        "meal_id": meal.id,
        "status": "completed",
        "extracted": extracted,
        "nutrition_totals": totals,
        "interactions": interactions,
        "progress": {
            "extraction": "done",
            "nutrition": "done" if totals else "pending",
            "interactions": "done",
        },
    }


@router.get("/status")
async def analysis_status(job_id: str | None = None) -> dict[str, object]:
    """Expose analysis progress/state."""
    return {
        "job_id": job_id or "latest",
        "status": "completed",
        "progress": 100,
        "steps": ["extraction", "nutrition", "interactions", "rules"],
    }
