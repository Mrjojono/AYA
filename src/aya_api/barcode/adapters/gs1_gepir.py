"""GS1 GEPIR adapter (stub)."""

from aya_api.barcode.schemas import SourceResult


class Gs1GepirAdapter:
    name = "gs1_gepir"
    license = "unknown"
    enabled = True

    def __init__(self, session=None):
        self.session = session

    async def lookup(self, gtin: str) -> SourceResult | None:
        # Stub - can be implemented later if needed
        return None

    async def search(self, name: str) -> list[SourceResult]:
        return []
