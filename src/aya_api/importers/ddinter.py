"""DDInter CSV importer."""

import csv
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.models import Drug, ImportReport, Interaction, RawDdinter

SOURCE = "DDInter"
SOURCE_VERSION = "2024"


async def import_ddinter(session: AsyncSession, csv_paths: list[Path]) -> ImportReport:
    """Import DDInter CSV files into raw and model tables."""
    drug_ids: dict[str, int] = {}
    severity_counts: Counter[str] = Counter()
    row_count = 0
    for path in csv_paths:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                a_id = row["DDInterID_A"]
                a_name = row["Drug_A"]
                b_id = row["DDInterID_B"]
                b_name = row["Drug_B"]
                level = row["Level"]
                severity_counts[level] += 1

                session.add(
                    RawDdinter(
                        ddinter_id_a=a_id,
                        drug_a=a_name,
                        ddinter_id_b=b_id,
                        drug_b=b_name,
                        level=level,
                        source=SOURCE,
                        source_version=SOURCE_VERSION,
                    )
                )

                for ext, name in ((a_id, a_name), (b_id, b_name)):
                    if ext not in drug_ids:
                        drug = await session.scalar(
                            select(Drug).where(Drug.external_id == ext)
                        )
                        if drug is None:
                            drug = Drug(external_id=ext, name=name)
                            session.add(drug)
                            await session.flush()
                        drug_ids[ext] = drug.id

                session.add(
                    Interaction(
                        drug_a_id=drug_ids[a_id],
                        drug_b_id=drug_ids[b_id],
                        severity=level,
                        source=SOURCE,
                        source_version=SOURCE_VERSION,
                    )
                )

    await session.flush()
    report = ImportReport(
        source=SOURCE,
        source_version=SOURCE_VERSION,
        row_count=row_count,
        distinct_drugs=len(drug_ids),
        severity_counts=dict(severity_counts).__repr__(),
    )
    session.add(report)
    await session.commit()
    return report
