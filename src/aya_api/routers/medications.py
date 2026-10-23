"""Medication search routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from rapidfuzz import process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Medication, MedicationSynonym

router = APIRouter(prefix="/medications", tags=["medications"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/search")
async def search(
    q: Annotated[str, Query(..., min_length=1)],
    session: SessionDep,
) -> list[dict[str, object]]:
    """Fuzzy search medications by name or synonym."""
    meds = (await session.execute(select(Medication))).scalars().all()
    syns = (await session.execute(select(MedicationSynonym))).scalars().all()
    keys = [m.commercial_name for m in meds] + [s.input_form for s in syns]
    matches = process.extract(q, keys, limit=5)
    results: list[dict[str, object]] = []
    for name, score, _ in matches:
        med = next((m for m in meds if m.commercial_name == name), None)
        if med is not None:
            results.append(
                {
                    "name": med.commercial_name,
                    "dci": med.dci,
                    "atc_code": med.atc_code,
                    "score": score,
                }
            )
            continue
        syn = next((s for s in syns if s.input_form == name), None)
        if syn is not None:
            med = next((m for m in meds if m.dci == syn.canonical_dci), None)
            if med is not None:
                results.append(
                    {
                        "name": med.commercial_name,
                        "dci": med.dci,
                        "atc_code": med.atc_code,
                        "score": score,
                    }
                )
    return results
