from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
HTML = SITE / "index.html"
STATIC = SITE / "static-data"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def require_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise AssertionError(f"Missing or empty deployment file: {path}")


def read_json(path: Path) -> dict:
    require_file(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in (
        HTML,
        SITE / "app.js",
        SITE / "styles.css",
        SITE / "config.js",
        SITE / "downloads" / "offer-evidence.xlsx",
        SITE / "last-updated.json",
        SITE / "_headers",
        SITE / "assets" / "alforaij_logo.png",
        SITE / "assets" / "kuwait_glass_cover.webp",
        SITE / "assets" / "alforaij-favicon-32.png",
        SITE / "assets" / "alforaij-favicon-v2.png",
        SITE / "assets" / "apple-touch-icon.png",
        SITE / "assets" / "favicon.ico",
        STATIC / "dashboard-summary.json",
        STATIC / "opportunities.json",
        STATIC / "market-matching.json",
        STATIC / "sources.json",
        STATIC / "health.json",
    ):
        require_file(path)

    dashboard = read_json(STATIC / "dashboard-summary.json")
    opportunities = read_json(STATIC / "opportunities.json")
    matching = read_json(STATIC / "market-matching.json")
    health = read_json(STATIC / "health.json")

    records = dashboard.get("records") or []
    if len(records) < 180:
        raise AssertionError(f"Dashboard snapshot is too small: {len(records)} records")
    if not dashboard.get("platforms"):
        raise AssertionError("Dashboard snapshot has no platform list")
    if not (dashboard.get("opportunities") or {}).get("items"):
        raise AssertionError("Dashboard snapshot has no opportunity items")
    if opportunities.get("totalScored", 0) <= 0:
        raise AssertionError("Opportunities snapshot has no scored records")
    if not opportunities.get("contributingSources"):
        raise AssertionError("Opportunities snapshot has no contributing sources")
    if not matching.get("requests"):
        raise AssertionError("Market matching snapshot has no requests")
    if health.get("records", 0) <= 0:
        raise AssertionError("Health snapshot has no record count")

    html_text = HTML.read_text(encoding="utf-8")
    required_markers = (
        'id="boardMetricFilter"',
        'id="boardPlatformFilter"',
        'id="chatInput"',
        'id="oppList"',
        'static-data/',
        'app.js',
        'styles.css',
    )
    missing = [marker for marker in required_markers if marker not in html_text and marker not in (SITE / "app.js").read_text(encoding="utf-8")]
    if missing:
        raise AssertionError(f"Missing platform features: {missing}")

    headers = (SITE / "_headers").read_text(encoding="utf-8")
    if "Content-Security-Policy" not in headers or "connect-src 'self'" not in headers:
        raise AssertionError("Deployment security headers must allow reading same-origin static-data")

    metadata = read_json(SITE / "last-updated.json")
    if metadata.get("record_count") != len(records):
        raise AssertionError("last-updated.json record count does not match dashboard-summary.json")

    print(json.dumps({
        "records": len(records),
        "opportunities_scored": opportunities.get("totalScored"),
        "opportunities_visible": len((dashboard.get("opportunities") or {}).get("items") or []),
        "market_requests": len(matching.get("requests") or []),
        "platforms": dashboard.get("platforms"),
        "status": "ok",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
