from __future__ import annotations

import json
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build_director_manager_report as report  # noqa: E402
import build_offer_evidence_browser as browser  # noqa: E402


def current_register_path() -> Path:
    files = sorted(
        path
        for path in browser.PLATFORM_DIR.glob("03_*.xlsx")
        if not path.name.startswith("~$")
    )
    if files:
        return files[0]
    return browser.PLATFORM_DIR / report.FINAL_EXCEL.name


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Keep the dashboard refresh lightweight: fetch API data and rebuild Excel only.
    # The full PDF/PPT report renderer is intentionally skipped for scheduled hosting.
    today = date.today()
    report.SNAPSHOT_DATE = today
    report.ensure_dirs()

    type_names, listings = report.fetch_all_data()
    metrics = report.build_analysis(type_names, listings)
    report.create_excel(metrics)

    target = current_register_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(report.EXCEL_PATH, target)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_date": today.isoformat(),
        "register": str(target),
        "source_register": str(report.EXCEL_PATH),
        "metrics": {
            "total_core": metrics.get("total_core"),
            "sale_count": metrics.get("sale_count"),
            "buy_count": metrics.get("buy_count"),
            "house_sale_count": metrics.get("house_sale_count"),
            "rent_count": metrics.get("rent_count"),
            "rent_request_count": metrics.get("rent_request_count"),
        },
    }
    (browser.PLATFORM_DIR / "99_refresh_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
