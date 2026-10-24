def _run_openfoodfacts() -> int:
    import asyncio
    from pathlib import Path

    from aya_api.config import get_settings
    from aya_api.db import AsyncSessionLocal
    from aya_api.importers import openfoodfacts

    get_settings()
    path = Path("databasesFiles/openfoodfacts.jsonl")
    if not path.exists():
        path = Path("databasesFiles/off.jsonl")

    async def main() -> int:
        async with AsyncSessionLocal() as session:
            return await openfoodfacts.import_from_jsonl(session, path)

    return asyncio.run(main())


def _run_lnme() -> int:
    import asyncio
    from pathlib import Path

    from aya_api.db import AsyncSessionLocal
    from aya_api.importers import lnme

    async def main() -> int:
        async with AsyncSessionLocal() as session:
            total = 0
            benin = Path("databasesFiles/lnme_benin_2018_adulte.csv")
            if benin.exists():
                total += await lnme.import_lnme_benin(session, benin)
            haiti = Path("databasesFiles/lnme_haiti_2020_demo.csv")
            if haiti.exists():
                total += await lnme.import_lnme_haiti(session, haiti)
            return total

    return asyncio.run(main())


if __name__ == "__main__":
    import sys

    if (len(sys.argv) > 1 and sys.argv[1] == "openfoodfacts") or (
        len(sys.argv) > 1 and sys.argv[1] == "off"
    ):
        count = _run_openfoodfacts()
    elif len(sys.argv) > 1 and sys.argv[1] in ("lnme", "benin", "haiti"):
        count = _run_lnme()
    else:
        msg = "usage: python -m aya_api.importers.cli <ddinter|wafct|oms|openfoodfacts|lnme>"
        raise SystemExit(msg)
