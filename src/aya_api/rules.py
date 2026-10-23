"""Rule matrix helpers."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.models import InteractionRule


async def build_matrix(session: AsyncSession) -> dict[tuple[str, str], str]:
    """Build a (drug, food) -> severity matrix from active rules."""
    stmt = select(InteractionRule).where(InteractionRule.active.is_(True))
    rules = (await session.execute(stmt)).scalars().all()
    return {(r.drug.lower(), r.food.lower()): r.severity for r in rules}


async def check(session: AsyncSession, drug: str, food: str) -> str | None:
    """Look up severity for a drug-food pair."""
    matrix = await build_matrix(session)
    return matrix.get((drug.lower(), food.lower()))
