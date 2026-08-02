from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
SITE_DIR = REPO_ROOT / "site"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build_offer_evidence_browser as browser  # noqa: E402
import build_dashboard_preview_v2 as dashboard_v2  # noqa: E402


def copy_required_file(source: Path, target: Path) -> None:
    if not source.exists() or source.stat().st_size == 0:
        raise FileNotFoundError(f"Missing generated file: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_static_metadata() -> None:
    payload_text = browser.PROPERTY_HTML_PATH.read_text(encoding="utf-8")
    payload_start = payload_text.find('<script id="payload" type="application/json">')
    payload_end = payload_text.find("</script>", payload_start)
    record_count = None
    if payload_start >= 0 and payload_end > payload_start:
        payload_start = payload_text.find(">", payload_start) + 1
        record_count = len(json.loads(payload_text[payload_start:payload_end]).get("records", []))
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "index.html",
        "dashboard_variant": "property-type-filter",
        "record_count": record_count,
        "downloads": ["downloads/offer-evidence.xlsx"],
    }
    (SITE_DIR / "last-updated.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (SITE_DIR / "robots.txt").write_text(
        "User-agent: *\nDisallow: /\n",
        encoding="utf-8",
    )
    (SITE_DIR / "_headers").write_text(
        "/*\n"
        "  X-Robots-Tag: noindex, nofollow\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  X-Frame-Options: DENY\n"
        "  Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; font-src 'self' data: https:; connect-src 'self'; upgrade-insecure-requests\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()\n"
        "  Strict-Transport-Security: max-age=31536000; includeSubDomains\n"
        "  Cache-Control: public, max-age=0, must-revalidate\n"
        "\n"
        "/index.html\n"
        "  Cache-Control: public, max-age=0, must-revalidate\n"
        "\n"
        "/last-updated.json\n"
        "  Cache-Control: no-store\n"
        "\n"
        "/downloads/*\n"
        "  Cache-Control: public, max-age=3600, must-revalidate\n"
        "\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=86400, stale-while-revalidate=604800\n",
        encoding="utf-8",
    )


def build_dashboard() -> None:
    try:
        browser.main()
    except PermissionError as exc:
        locked_output = str(browser.XLSX_PATH) in str(exc) or browser.XLSX_PATH.name in str(exc)
        if not locked_output or not browser.PROPERTY_HTML_PATH.exists():
            raise
        print(
            "Warning: dashboard Excel is locked locally; "
            "continuing with the existing Excel copy for the static site.",
            file=sys.stderr,
        )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    build_dashboard()

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    copy_required_file(browser.PROPERTY_HTML_PATH, SITE_DIR / "index.html")
    copy_required_file(browser.XLSX_PATH, SITE_DIR / "downloads" / "offer-evidence.xlsx")
    generated_assets = browser.OUTPUT_DIR / "assets"
    if not generated_assets.exists():
        raise FileNotFoundError(f"Missing generated assets: {generated_assets}")
    shutil.copytree(generated_assets, SITE_DIR / "assets")
    write_static_metadata()

    preview_html = dashboard_v2.build_preview()
    preview_dir = preview_html.parent
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    shutil.copytree(preview_dir, SITE_DIR)

    print(
        json.dumps(
            {
                "site": str(SITE_DIR),
                "entrypoint": str(SITE_DIR / "index.html"),
                "files": sorted(path.name for path in SITE_DIR.iterdir()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
