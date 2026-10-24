"""Product/barcode routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.barcode.orchestrator import BarcodeOrchestrator
from aya_api.db import get_session
from aya_api.models import BarcodeLookupAttempt, Product

router = APIRouter(prefix="/products", tags=["products"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/barcode/{ean}")
async def get_by_barcode(ean: str, session: SessionDep) -> dict[str, object]:
    """Get product by barcode/EAN (uses orchestrator)."""
    orch = BarcodeOrchestrator(session)
    result, attempts = await orch.resolve(ean)
    if result and result.found:
        # update cache stats if exists
        stmt = select(Product).where(Product.barcode == result.gtin)
        res = await session.execute(stmt)
        prod = res.scalars().first()
        if prod:
            prod.last_consulted_at = datetime.utcnow()
            await session.commit()
        return {
            "barcode": result.gtin,
            "product_name": result.name,
            "brands": result.brand,
            "ingredients_text": result.ingredients_text,
            "categories": result.category,
            "nutrients": result.nutrients or {},
            "nutriscore_grade": result.nutriscore_grade,
            "nova_group": result.nova_group,
            "image_url": result.image_url,
            "countries": result.countries,
            "confidence": result.confidence,
            "data_quality": result.data_quality,
            "source": result.source,
            "license": result.license,
            "attempts": attempts,
        }
    # fallback to direct lookup
    stmt = select(Product).where(Product.barcode == ean.strip().replace("-", ""))
    result2 = await session.execute(stmt)
    prod = result2.scalars().first()
    if prod is None:
        raise HTTPException(status_code=404, detail="Product not found")
    prod.last_consulted_at = datetime.utcnow()
    await session.commit()
    return {
        "barcode": prod.barcode,
        "product_name": prod.product_name,
        "brands": prod.brands,
        "ingredients_text": prod.ingredients_text,
        "categories": prod.categories,
        "nutrients": prod.nutrients,
        "nutriscore_grade": prod.nutriscore_grade,
        "nova_group": prod.nova_group,
        "image_url": prod.image_url,
        "countries": prod.countries,
        "confidence": prod.confidence,
        "data_quality": prod.data_quality,
        "source": prod.source,
        "license": prod.license,
        "attempts": attempts,
    }


@router.get("/barcode/{ean}/resolve")
async def resolve_barcode(ean: str, session: SessionDep) -> dict[str, object]:
    """Resolve barcode via orchestrator with full trace."""
    orch = BarcodeOrchestrator(session)
    result, attempts = await orch.resolve(ean)
    if result and result.found:
        return {
            "found": True,
            "result": result.model_dump(),
            "attempts": attempts,
        }
    return {"found": False, "result": None, "attempts": attempts}


@router.post("/lookup")
async def lookup_barcode(barcode: str, session: SessionDep) -> dict[str, object]:
    """Lookup product by barcode."""
    return await get_by_barcode(barcode, session)


@router.post("/coverage/run")
async def coverage_run(gtins: list[str], session: SessionDep) -> dict[str, object]:
    """Run coverage test for a list of GTINs."""
    orch = BarcodeOrchestrator(session)
    results = []
    for gtin in gtins:
        res, attempts = await orch.resolve(gtin)
        results.append({"gtin": gtin.strip(), "found": bool(res and res.found), "chosen_source": res.source if res else None, "attempts": attempts})
    return {"count": len(results), "results": results}


@router.get("/coverage/matrix")
async def coverage_matrix(session: SessionDep) -> dict[str, object]:
    """Build coverage matrix from lookup attempts."""
    # Get all GTINs
    gtins_stmt = select(BarcodeLookupAttempt.gtin).distinct().order_by(BarcodeLookupAttempt.gtin)
    gtins_res = await session.execute(gtins_stmt)
    gtins = [g[0] for g in gtins_res.all()]
    matrix = []
    for gtin in gtins:
        stmt = select(BarcodeLookupAttempt).where(BarcodeLookupAttempt.gtin == gtin).order_by(BarcodeLookupAttempt.created_at)
        res = await session.execute(stmt)
        attempts = res.scalars().all()
        row = {"gtin": gtin}
        chosen = None
        for a in attempts:
            row[a.source] = "oui" if a.found else "non"
            if a.chosen and a.found:
                chosen = a.source
        row["resultat_retenu"] = chosen or "aucun"
        matrix.append(row)
    sources = []
    if matrix:
        for k in matrix[0].keys():
            if k not in ("gtin", "resultat_retenu"):
                sources.append(k)
    return {"sources": sources, "matrix": matrix, "count": len(matrix)}


@router.get("/coverage/stats")
async def coverage_stats(session: SessionDep) -> dict[str, object]:
    """Coverage statistics by source."""
    sources_stmt = select(BarcodeLookupAttempt.source).distinct()
    sources_res = await session.execute(sources_stmt)
    sources = [s[0] for s in sources_res.all()]
    stats = {}
    for src in sources:
        total = await session.execute(select(func.count(BarcodeLookupAttempt.id)).where(BarcodeLookupAttempt.source == src))
        found = await session.execute(select(func.count(BarcodeLookupAttempt.id)).where(BarcodeLookupAttempt.source == src, BarcodeLookupAttempt.found.is_(True)))
        errors = await session.execute(select(func.count(BarcodeLookupAttempt.id)).where(BarcodeLookupAttempt.source == src, BarcodeLookupAttempt.error.is_not(None)))
        chosen = await session.execute(select(func.count(BarcodeLookupAttempt.id)).where(BarcodeLookupAttempt.source == src, BarcodeLookupAttempt.chosen.is_(True)))
        stats[src] = {
            "total_attempts": total.scalar() or 0,
            "found": found.scalar() or 0,
            "errors": errors.scalar() or 0,
            "chosen": chosen.scalar() or 0,
        }
    return {"stats": stats}


@router.get("/cache/stats")
async def cache_stats(session: SessionDep) -> dict[str, object]:
    """Stats about cached products."""
    total = await session.execute(select(func.count(Product.id)))
    total_count = total.scalar() or 0
    high = await session.execute(select(func.count(Product.id)).where(Product.data_quality == "high"))
    medium = await session.execute(select(func.count(Product.id)).where(Product.data_quality == "medium"))
    low = await session.execute(select(func.count(Product.id)).where(Product.data_quality == "low"))
    consulted = await session.execute(select(func.count(Product.id)).where(Product.last_consulted_at.is_not(None)))
    return {
        "total_cached": total_count,
        "quality": {
            "high": high.scalar() or 0,
            "medium": medium.scalar() or 0,
            "low": low.scalar() or 0,
        },
        "consulted_count": consulted.scalar() or 0,
        "coverage": {"cached_products": total_count},
    }

