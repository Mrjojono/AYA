"""Adapter registry."""

from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.barcode.adapters.cache import CacheAdapter
from aya_api.barcode.adapters.commercial import CommercialAdapter
from aya_api.barcode.adapters.gs1_gepir import Gs1GepirAdapter
from aya_api.barcode.adapters.internal import InternalAdapter
from aya_api.barcode.adapters.off_local import OffLocalAdapter


def build_adapters(session: AsyncSession) -> dict:
    """Build all adapters."""
    adapters = {
        "cache": CacheAdapter(session),
        "interne_valide": InternalAdapter(session),
        "off_local": OffLocalAdapter(session),
        "gs1_gepir": Gs1GepirAdapter(session),
        "api_commerciale": CommercialAdapter(session),
    }
    return adapters
