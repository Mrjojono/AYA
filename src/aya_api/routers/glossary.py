"""Glossary and decomposition routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Glossary

router = APIRouter(prefix="/glossary", tags=["glossary"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/lookup")
async def lookup(term: str, session: SessionDep) -> list[dict[str, object]]:
    """Look up a term in the glossary."""
    stmt = select(Glossary)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        {"term": r.term, "canonical": r.canonical, "components": r.components}
        for r in rows
        if term.lower() in r.term.lower()
    ]
