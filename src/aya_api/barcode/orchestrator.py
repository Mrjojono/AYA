"""Barcode orchestrator with tracing."""

import time

from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.barcode.config import load_sources_config
from aya_api.barcode.registry import build_adapters
from aya_api.barcode.schemas import SourceResult
from aya_api.models import BarcodeLookupAttempt


class BarcodeOrchestrator:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.adapters = build_adapters(session)
        self.config = load_sources_config()

    async def resolve(self, gtin: str) -> tuple[SourceResult | None, list[dict]]:
        """Resolve barcode by trying sources in order."""
        gtin_norm = gtin.strip().replace("-", "").replace(" ", "")
        order = self.config.get("barcode", {}).get(
            "order", ["cache", "interne_valide", "off_local"]
        )
        stop_on_first = self.config.get("barcode", {}).get("stop_on_first_valid", True)
        attempts = []
        chosen_result = None

        for source_name in order:
            adapter = self.adapters.get(source_name)
            if not adapter:
                continue
            if hasattr(adapter, "enabled") and not adapter.enabled:
                continue
            start = time.time()
            error = None
            result = None
            try:
                result = await adapter.lookup(gtin_norm)
            except Exception as e:
                error = str(e)
            latency_ms = int((time.time() - start) * 1000)
            found = bool(result and result.found)
            license = getattr(
                adapter, "license", result.license if result else "unknown"
            )

            attempt = BarcodeLookupAttempt(
                gtin=gtin_norm,
                source=source_name,
                found=found,
                latency_ms=latency_ms,
                error=error,
                license=license,
                chosen=False,
                confidence=result.confidence if result else None,
            )
            self.session.add(attempt)
            attempts.append(
                {
                    "source": source_name,
                    "found": found,
                    "latency_ms": latency_ms,
                    "error": error,
                    "license": license,
                    "confidence": result.confidence if result else None,
                }
            )
            if found and result:
                chosen_result = result
                attempt.chosen = True
                if stop_on_first:
                    break
        await self.session.commit()
        return chosen_result, attempts

    async def search(self, name: str) -> list[SourceResult]:
        """Search across sources."""
        results = []
        order = self.config.get("search", {}).get(
            "order", ["interne_valide", "off_local"]
        )
        for source_name in order:
            adapter = self.adapters.get(source_name)
            if not adapter or (hasattr(adapter, "enabled") and not adapter.enabled):
                continue
            try:
                res = await adapter.search(name)
                results.extend(res)
            except Exception:
                continue
        return results
