"""LNME (Bénin/Haiti) importer."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

from sqlalchemy import select

from aya_api.models import ImportReport, Medication

if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.ext.asyncio import AsyncSession


async def import_lnme_benin(session: AsyncSession, path: Path) -> int:
    """Import LNME Bénin adult list."""
    count = 0
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dci = (row.get("dci") or "").strip()
            if not dci:
                continue
            commercial = (
                row.get("exemples_specialites_benin") or row.get("nom_commercial") or ""
            ).strip()
            forme = (row.get("forme_dosage") or "").strip()
            atc = (row.get("atc_code") or "").strip() or None
            section = (row.get("section_lnme") or "").strip()
            stmt = select(Medication).where(
                Medication.dci.ilike(dci), Medication.commercial_name == commercial
            )
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                if not existing.atc_code and atc:
                    existing.atc_code = atc
                continue
            med = Medication(
                commercial_name=commercial or dci,
                dci=dci,
                active_substances=dci,
                form=forme or None,
                dosage=None,
                atc_code=atc,
                therapeutic_class=section or "LNME_BENIN_2018",
                source="LNME_BENIN_2018_DEMO",
            )
            session.add(med)
            count += 1
    report = ImportReport(
        source="lnme_benin",
        source_version="2018_adulte",
        row_count=count,
        distinct_drugs=count,
        severity_counts="{}",
    )
    session.add(report)
    await session.commit()
    return count


async def import_lnme_haiti(session: AsyncSession, path: Path) -> int:
    """Import LNME Haiti demo list."""
    count = 0
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dci = (row.get("dci") or "").strip()
            if not dci:
                continue
            commercial = (row.get("nom_commercial") or "").strip() or dci
            forme = (row.get("forme") or "").strip()
            dosage = (row.get("dosage") or "").strip()
            atc = (row.get("atc_code") or "").strip() or None
            classe = (row.get("classe_lnme") or "").strip()
            stmt = select(Medication).where(
                Medication.dci.ilike(dci), Medication.commercial_name == commercial
            )
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                if not existing.atc_code and atc:
                    existing.atc_code = atc
                continue
            med = Medication(
                commercial_name=commercial,
                dci=dci,
                active_substances=dci,
                form=forme or None,
                dosage=dosage or None,
                atc_code=atc,
                therapeutic_class=classe or "LNME_HAITI_2020",
                source="LNME_HAITI_2020_DEMO",
            )
            session.add(med)
            count += 1
    report = ImportReport(
        source="lnme_haiti",
        source_version="2020_demo",
        row_count=count,
        distinct_drugs=count,
        severity_counts="{}",
    )
    session.add(report)
    await session.commit()
    return count
