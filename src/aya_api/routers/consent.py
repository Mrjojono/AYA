"""Consent routes."""

from typing import Annotated, ClassVar

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Consent

router = APIRouter(prefix="/consent", tags=["consent"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class ConsentRequest(BaseModel):
    """Consent request."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    session_id: str = "anonymous"
    purpose: str
    granted: bool


class ConsentResponse(BaseModel):
    """Consent response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int
    session_id: str
    purpose: str
    granted: bool


@router.post("", status_code=201)
async def set_consent(payload: ConsentRequest, session: SessionDep) -> ConsentResponse:
    """Set consent for a specific purpose."""
    consent = Consent(
        session_id=payload.session_id, purpose=payload.purpose, granted=payload.granted
    )
    session.add(consent)
    await session.commit()
    await session.refresh(consent)
    return ConsentResponse(
        id=consent.id,
        session_id=consent.session_id,
        purpose=consent.purpose,
        granted=consent.granted,
    )


@router.get("")
async def get_consents(
    session_id: str = "anonymous", session: SessionDep = None
) -> list[ConsentResponse]:
    """Get all consents for a session."""
    stmt = select(Consent).where(Consent.session_id == session_id)
    result = await session.execute(stmt)
    consents = result.scalars().all()
    return [
        ConsentResponse(
            id=c.id, session_id=c.session_id, purpose=c.purpose, granted=c.granted
        )
        for c in consents
    ]
