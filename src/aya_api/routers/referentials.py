"""Referential data routes."""

from typing import ClassVar

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/referentials", tags=["referentials"])


class ItemList(BaseModel):
    """List of items."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    items: list[str]


CONDITIONS = [
    "diabète",
    "hypertension",
    "insuffisance rénale",
    "grossesse",
    "allergie",
]

ALLERGENS = [
    "arachide",
    "gluten",
    "lait",
    "œuf",
    "fruits de mer",
    "soja",
    "noix",
]


@router.get("/conditions")
async def get_conditions() -> ItemList:
    """List common health conditions."""
    return ItemList(items=CONDITIONS)


@router.get("/allergens")
async def get_allergens() -> ItemList:
    """List common allergens."""
    return ItemList(items=ALLERGENS)
