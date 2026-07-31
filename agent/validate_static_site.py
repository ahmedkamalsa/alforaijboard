from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
HTML = SITE / "index.html"


def require_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise AssertionError(f"Missing or empty deployment file: {path}")


def embedded_payload() -> dict:
    text = HTML.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="payload" type="application/json">(.*?)</script>',
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError("Embedded dashboard payload was not found")
    return json.loads(match.group(1))


def main() -> None:
    for path in (
        HTML,
        SITE / "downloads" / "offer-evidence.xlsx",
        SITE / "last-updated.json",
        SITE / "_headers",
        SITE / "assets" / "alforaij_logo.png",
        SITE / "assets" / "kuwait_glass_cover.webp",
        SITE / "assets" / "alforaij-favicon-32.png",
        SITE / "assets" / "alforaij-favicon-v2.png",
        SITE / "assets" / "apple-touch-icon.png",
        SITE / "assets" / "favicon.ico",
    ):
        require_file(path)

    payload = embedded_payload()
    records = payload.get("records") or []
    metrics = {item["metric"]: item["count"] for item in payload.get("metrics") or []}
    governors = payload.get("governors") or []

    if not records:
        raise AssertionError("Dashboard payload contains no records")
    codes = [row.get("code") for row in records]
    if len(codes) != len(set(codes)):
        raise AssertionError("Dashboard payload contains duplicate advertisement codes")

    transaction_total = sum(metrics.get(key, 0) for key in ("sell", "buy", "rent", "rent_request"))
    if transaction_total != metrics.get("movement") or transaction_total != len(records):
        raise AssertionError(
            f"Metric mismatch: movement={metrics.get('movement')} "
            f"transactions={transaction_total} records={len(records)}"
        )
    if sum(row.get("movement", 0) for row in governors) != len(records):
        raise AssertionError("Governorate totals do not match the record count")
    localized_images = sum(
        str(row.get("imageUrl") or "").startswith("assets/listings/")
        for row in records
    )
    if localized_images < int(len(records) * 0.9):
        raise AssertionError(
            f"Too few optimized local listing images: {localized_images}/{len(records)}"
        )

    for row in records:
        original_url = str(row.get("originalUrl") or "")
        if row.get("originalAvailable") and not re.fullmatch(
            r"https://front\.alforaij\.com/Listing/Detail/\d+",
            original_url,
        ):
            raise AssertionError(f"Invalid public advertisement URL for {row.get('code')}: {original_url}")

    html_text = HTML.read_text(encoding="utf-8")
    required_markers = (
        'id="listingModeFilter"',
        'id="loadMoreButton"',
        'id="downloadCsvButton"',
        'class="table-scroll"',
        "RESULT_PAGE_SIZE = 24",
    )
    missing = [marker for marker in required_markers if marker not in html_text]
    if missing:
        raise AssertionError(f"Missing dashboard features: {missing}")

    metadata = json.loads((SITE / "last-updated.json").read_text(encoding="utf-8"))
    if metadata.get("record_count") != len(records):
        raise AssertionError("last-updated.json record count does not match the dashboard")
    if "Content-Security-Policy" not in (SITE / "_headers").read_text(encoding="utf-8"):
        raise AssertionError("Deployment security headers are incomplete")

    print(
        json.dumps(
            {
                "records": len(records),
                "metrics": metrics,
                "governorates": len(governors),
                "localized_images": localized_images,
                "status": "ok",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
