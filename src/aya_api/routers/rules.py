"""Rule checking routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.rules import check

router = APIRouter(prefix="/rules", tags=["rules"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/check")
async def check_rule(drug: str, food: str, session: SessionDep) -> dict[str, object]:
    """Check interaction severity for a drug-food pair."""
    severity = await check(session, drug, food)
    return {"drug": drug, "food": food, "severity": severity}
