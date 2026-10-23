"""Database engine and request-session dependency."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from aya_api.config import get_settings


class Base(DeclarativeBase):
    """Base class for AYA database models."""


engine = create_async_engine(
    get_settings().database_url.unicode_string(),
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one database session per request."""
    async with session_factory() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
