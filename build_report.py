#!/usr/bin/env python3
"""Build a concise health report from the latest cron_results_local.json entry."""
import json

path = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"
with open(path) as f:
    entries = json.load(f)

if not entries:
    print("[SILENT]")
    exit(0)

latest = entries[-1]
checks = latest.get("checks", {})

lines = []
lines.append(f"الساعة: {latest['timestamp']}")
lines.append(f"الحالة: {latest['overall']}")
lines.append("")

for key, check in checks.items():
    name = key.upper()
    status = check.get("status", "UNKNOWN")
    sev = check.get("severity", "info")
    details = check.get("details", "")
    icon = {"error": "🔴", "warning": "🟡", "info": "🟢"}.get(sev, "⚪")
    lines.append(f"{icon} [{name}] {status}")
    lines.append(f"   {details}")
    lines.append("")

# Summary
alerts = []
for k, c in checks.items():
    if c.get("severity") == "error":
        alerts.append(f"  🔴 {k}: {c['status']} — {c['details']}")

lines.append("=" * 50)
if alerts:
    lines.append(f"⚠ {len(alerts)} ERROR(S) تحتاج اهتمام فورى:")
    lines.extend(alerts)
else:
    lines.append("كل الأنظمة تعمل طبيعي.")

# Disk is borderline — mention
if checks.get("disk", {}).get("status") in ("OK", "WARN"):
    lines.append("")
    lines.append("ملاحظة: المساحةを担当 C: عند الحد (10%) — مراقبة مستمرة.")

report = "\n".join(lines)
print(report)

# Also write to a plain text file for quick reading
with open("/c/Users/hello/alforaijboard-gh/_cron_health_latest.txt", "w") as f:
    f.write(report)
