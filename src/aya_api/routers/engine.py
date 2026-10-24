"""Evaluation engine routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import InteractionRule, Profile
from aya_api.rules import check

router = APIRouter(prefix="/engine", tags=["engine"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/evaluate")
async def evaluate(drug: str, food: str, session_id: str = "anonymous", session: SessionDep = None) -> dict[str, object]:
    """Evaluate a drug-food pair and return a three-tier outcome."""
    severity = await check(session, drug, food)
    if severity is None:
        outcome = "unavailable"
    elif severity and severity.lower() in {"major", "red", "contraindicated", "high"}:
        outcome = "red"
    elif severity and severity.lower() in {"moderate", "orange", "medium"}:
        outcome = "orange"
    else:
        outcome = "orange"

    alerts: list[str] = []
    # Check allergies and conditions from profile
    stmt = select(Profile).where(Profile.session_id == session_id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    if profile:
        if profile.allergies:
            allergies = [a.strip().lower() for a in profile.allergies.split(",") if a.strip()]
            food_l = food.lower()
            if any(a and a in food_l for a in allergies):
                alerts.append(f"Allergène potentiel détecté pour {food}")
                outcome = "red"
        if profile.conditions:
            alerts.append(f"Profil : conditions déclarées à considérer - {profile.conditions}")

    # Get rule metadata for sources/versions
    rule_stmt = select(InteractionRule).where(
        InteractionRule.drug.ilike(f"%{drug}%"), InteractionRule.food.ilike(f"%{food}%")
    )
    rule = (await session.execute(rule_stmt)).scalars().first()
    sources = []
    if rule and rule.source:
        sources.append(rule.source)
    if rule:
        sources.append(f"rule_id:{rule.id}")
    # Ensure we always consign sources/versions
    if not sources:
        sources = ["unknown"]

    return {
        "drug": drug,
        "food": food,
        "severity": severity,
        "outcome": outcome,
        "alerts": alerts,
        "sources": sources,
        "versions": {"rules_version": "v1", "sources": sources},
    }

