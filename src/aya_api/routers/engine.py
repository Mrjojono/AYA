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

_MAJOR = {"major", "red", "contraindicated", "high"}
_MOD = {"moderate", "orange", "medium"}


def _map_severity(severity: str | None) -> str:
    if severity is None:
        return "unavailable"
    sev_l = severity.lower()
    if sev_l in _MAJOR:
        return "red"
    if sev_l in _MOD:
        return "orange"
    return "orange"


async def _check_allergies(
    session: SessionDep, session_id: str, food: str
) -> list[str]:
    alerts: list[str] = []
    stmt = select(Profile).where(Profile.session_id == session_id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        return alerts
    if profile.allergies:
        allergies = [
            a.strip().lower() for a in profile.allergies.split(",") if a.strip()
        ]
        food_l = food.lower()
        if any(a and a in food_l for a in allergies):
            alerts.append(f"Allergène potentiel détecté pour {food}")
    if profile.conditions:
        alerts.append(f"Profil : conditions déclarées à considérer - {profile.conditions}")
    return alerts


async def _get_sources(session: SessionDep, drug: str, food: str) -> list[str]:
    rule_stmt = select(InteractionRule).where(
        InteractionRule.drug.ilike(f"%{drug}%"), InteractionRule.food.ilike(f"%{food}%")
    )
    rule = (await session.execute(rule_stmt)).scalars().first()
    sources = []
    if rule and rule.source:
        sources.append(rule.source)
    if rule:
        sources.append(f"rule_id:{rule.id}")
    if not sources:
        sources = ["unknown"]
    return sources


@router.get("/evaluate")
async def evaluate(
    drug: str,
    food: str,
    session: SessionDep,
    session_id: str = "anonymous",
) -> dict[str, object]:
    """Evaluate a drug-food pair and return a three-tier outcome."""
    severity = await check(session, drug, food)
    outcome = _map_severity(severity)

    alerts = await _check_allergies(session, session_id, food)
    if any("Allergène" in a for a in alerts):
        outcome = "red"

    sources = await _get_sources(session, drug, food)

    return {
        "drug": drug,
        "food": food,
        "severity": severity,
        "outcome": outcome,
        "alerts": alerts,
        "sources": sources,
        "versions": {"rules_version": "v1", "sources": sources},
    }
