"""Medication search routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
                    "active_substances": med.active_substances,
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
                        "active_substances": med.active_substances,
                        "score": score,
                    }
                )
    return results


@router.get("/related")
async def related(
    dci: Annotated[str | None, Query()] = None,
    name: Annotated[str | None, Query()] = None,
    session: SessionDep = None,
) -> list[dict[str, object]]:
    """Get medications related to the same active substance/DCI."""
    if dci is None and name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="dci or name required"
        )
    stmt = select(Medication)
    meds = (await session.execute(stmt)).scalars().all()
    if dci:
        target_dci = dci.lower()
        related_meds = [m for m in meds if m.dci and m.dci.lower() == target_dci]
    else:
        # find by name
        keys = [m.commercial_name for m in meds]
        matches = process.extract(name or "", keys, limit=1)
        if not matches:
            return []
        match_name = matches[0][0]
        med = next((m for m in meds if m.commercial_name == match_name), None)
        if not med or not med.dci:
            return []
        related_meds = [m for m in meds if m.dci and m.dci.lower() == med.dci.lower()]
    return [
        {
            "name": m.commercial_name,
            "dci": m.dci,
            "atc_code": m.atc_code,
            "active_substances": m.active_substances,
            "form": m.form,
            "dosage": m.dosage,
        }
        for m in related_meds
    ]
