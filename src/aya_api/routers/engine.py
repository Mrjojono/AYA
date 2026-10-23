"""Evaluation engine routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.rules import check

router = APIRouter(prefix="/engine", tags=["engine"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/evaluate")
async def evaluate(drug: str, food: str, session: SessionDep) -> dict[str, object]:
    """Evaluate a drug-food pair and return a three-tier outcome."""
    severity = await check(session, drug, food)
    if severity is None:
        outcome = "unavailable"
    elif severity.lower() in {"major", "red"}:
        outcome = "red"
    else:
        outcome = "orange"
    return {"drug": drug, "food": food, "severity": severity, "outcome": outcome}
