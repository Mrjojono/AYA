"""WHO/FAO threshold importer."""

import csv
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from aya_api.models import OmsThreshold

SOURCE_VERSION = "WHO/FAO 2004"


async def import_oms_thresholds(session: AsyncSession, csv_path: Path) -> int:
    """Import WHO thresholds CSV."""
    count = 0
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.add(
                OmsThreshold(
                    nutrient=row["nutrient"],
                    unit=row["unit"],
                    population_group=row["group"],
                    rni_low=float(row["rni_low"]) if row.get("rni_low") else None,
                    rni_high=float(row["rni_high"]) if row.get("rni_high") else None,
                    value_type=row.get("value_type", "RNI"),
                    bioavailability=row.get("bioavailability") or None,
                    source_version=SOURCE_VERSION,
                )
            )
            count += 1
    await session.commit()
    return count
