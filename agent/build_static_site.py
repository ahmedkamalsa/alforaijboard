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


def copy_required_file(source: Path, target: Path) -> None:
    if not source.exists() or source.stat().st_size == 0:
        raise FileNotFoundError(f"Missing generated file: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_static_metadata() -> None:
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "index.html",
        "dashboard_variant": "property-type-filter",
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
        "  Referrer-Policy: no-referrer\n",
        encoding="utf-8",
    )
    (SITE_DIR / "README.txt").write_text(
        "لوحة استعراض الأرقام والعروض الفعلية.\n"
        "افتح index.html بعد النشر. ملف Excel المساند داخل downloads.\n"
        "الصفحة لا تحتاج قاعدة بيانات في هذه المرحلة؛ البيانات مدمجة داخل HTML عند وقت البناء.\n",
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
    copy_required_file(browser.HTML_PATH, SITE_DIR / "dashboard-original.html")
    copy_required_file(browser.XLSX_PATH, SITE_DIR / "downloads" / "offer-evidence.xlsx")
    write_static_metadata()

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
