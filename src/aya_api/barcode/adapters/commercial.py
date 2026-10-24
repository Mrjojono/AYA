"""Commercial API adapter (disabled by default)."""

from aya_api.barcode.config import is_commercial_enabled
from aya_api.barcode.schemas import SourceResult


class CommercialAdapter:
    name = "api_commerciale"
    license = "commercial"
    enabled = False

    def __init__(self, session=None) -> None:
        self.enabled = is_commercial_enabled()
        self.session = session

    async def lookup(self, gtin: str) -> SourceResult | None:
        if not self.enabled:
            return None
        # Not implemented - only enable if CGU validated and budget available
        return None

    async def search(self, name: str) -> list[SourceResult]:
        if not self.enabled:
            return []
        return []
