"""Base adapter interface."""

from typing import Protocol

from aya_api.barcode.schemas import SourceResult


class BarcodeSource(Protocol):
    """Protocol for barcode lookup sources."""

    name: str
    license: str
    enabled: bool

    async def lookup(self, gtin: str) -> SourceResult | None: ...

    async def search(self, name: str) -> list[SourceResult]: ...
