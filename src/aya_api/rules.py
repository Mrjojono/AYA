"""Rule matrix helpers."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.models import InteractionRule


async def build_matrix(session: AsyncSession) -> dict[tuple[str, str], str]:
    """Build a (drug, food) -> severity matrix from active rules."""
    stmt = select(InteractionRule).where(InteractionRule.active.is_(True))
    rules = (await session.execute(stmt)).scalars().all()
    matrix: dict[tuple[str, str], str] = {}
    for r in rules:
        matrix[(r.drug.lower().strip(), r.food.lower().strip())] = r.severity
    return matrix


async def check(session: AsyncSession, drug: str, food: str) -> str | None:
    """Look up severity for a drug-food pair."""
    matrix = await build_matrix(session)
    key = (drug.lower().strip(), food.lower().strip())
    if key in matrix:
        return matrix[key]
    # Try partial matches
    for (d, f), sev in matrix.items():
        if (d in key[0] or key[0] in d) and (f in key[1] or key[1] in f):
            return sev
    return None


async def get_matrix(session: AsyncSession) -> list[dict[str, str]]:
    """Return full matrix as list."""
    stmt = select(InteractionRule).where(InteractionRule.active.is_(True))
    rules = (await session.execute(stmt)).scalars().all()
    return [{"drug": r.drug, "food": r.food, "severity": r.severity, "source": r.source} for r in rules]

