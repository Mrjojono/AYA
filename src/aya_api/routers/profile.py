"""Profile routes."""

from typing import Annotated, ClassVar

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.db import get_session
from aya_api.models import Profile

router = APIRouter(prefix="/profile", tags=["profile"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class ProfileCreate(BaseModel):
    """Profile creation payload."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    session_id: str = "anonymous"
    age: int
    weight_kg: float | None = None
    height_cm: float | None = None
    conditions: str | None = None
    allergies: str | None = None
    diet: str | None = None
    medications: str | None = None


class ProfileResponse(BaseModel):
    """Profile response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int
    session_id: str
    age: int
    weight_kg: float | None = None
    height_cm: float | None = None
    conditions: str | None = None
    allergies: str | None = None
    diet: str | None = None
    medications: str | None = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: ProfileCreate, session: SessionDep
) -> ProfileResponse:
    """Create a user health profile (age required)."""
    profile = Profile(
        session_id=payload.session_id,
        age=payload.age,
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        conditions=payload.conditions,
        allergies=payload.allergies,
        diet=payload.diet,
        medications=payload.medications,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return ProfileResponse(
        id=profile.id,
        session_id=profile.session_id,
        age=profile.age,
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        conditions=profile.conditions,
        allergies=profile.allergies,
        diet=profile.diet,
        medications=profile.medications,
    )


@router.get("")
async def get_profile(
    session_id: str = "anonymous", session: SessionDep = None
) -> ProfileResponse:
    """Get profile by session_id."""
    stmt = select(Profile).where(Profile.session_id == session_id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
    return ProfileResponse(
        id=profile.id,
        session_id=profile.session_id,
        age=profile.age,
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        conditions=profile.conditions,
        allergies=profile.allergies,
        diet=profile.diet,
        medications=profile.medications,
    )


@router.put("")
async def update_profile(
    payload: ProfileCreate, session_id: str = "anonymous", session: SessionDep = None
) -> ProfileResponse:
    """Update profile."""
    stmt = select(Profile).where(Profile.session_id == session_id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    if profile is None:
        profile = Profile(
            session_id=session_id,
            age=payload.age,
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            conditions=payload.conditions,
            allergies=payload.allergies,
            diet=payload.diet,
            medications=payload.medications,
        )
        session.add(profile)
    else:
        profile.age = payload.age
        profile.weight_kg = payload.weight_kg
        profile.height_cm = payload.height_cm
        profile.conditions = payload.conditions
        profile.allergies = payload.allergies
        profile.diet = payload.diet
        profile.medications = payload.medications
    await session.commit()
    await session.refresh(profile)
    return ProfileResponse(
        id=profile.id,
        session_id=profile.session_id,
        age=profile.age,
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        conditions=profile.conditions,
        allergies=profile.allergies,
        diet=profile.diet,
        medications=profile.medications,
    )
