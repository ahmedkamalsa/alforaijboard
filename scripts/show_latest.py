import json
import sys
import os
from datetime import datetime, timezone, timedelta

KWT = timezone(timedelta(hours=3))

def timestamp():
    return datetime.now(KWT).strftime("%Y-%m-%d %H:%M:%S")

def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

def build(d, lang="ar"):
    loc = d.get("_local") or {}
    lines = []
    stamp = timestamp()
    if lang == "ar":
        lines.append(f"تقرير الفحص الصحي - {stamp} (توقيت الكويت)")
        lines.append("")
        lines.append(f"الحالة العامة: {loc.get('overall', 'UNKNOWN')} (3 مشاكل)")
        lines.append("")
        lines.append(f"1) Docker: {d.get('docker')}")
        lines.append(f"   التفاصيل: {loc.get('docker_detail', '')}")
        lines.append("")
        lines.append(f"2) الذاكرة (RAM): {'طبيعي OK' if d.get('ram_ok') == 'yes' else 'check'}")
        lines.append(f"   حر: {d.get('ram_free_mb')} ميجابايت / إجمالي {d.get('ram_total_mb')} ميجابايت")
        lines.append(f"   التفاصيل: {loc.get('ram_detail', '')}")
        lines.append("")
        lines.append(f"3) عمليات Hermes: {'يعمل OK' if d.get('hermes_agents') else 'لم يُعثر عليه'}")
        lines.append(f"   التفاصيل: {d.get('hermes_agents')}")
        lines.append("")
        lines.append(f"4) ملف C:/Users/hello: {'تحذير WARN' if d.get('disk_warn') == 'yes' else 'طبيعي OK'}")
        lines.append(f"   حر: {d.get('disk_free_gb')} جيجابايت / إجمالي {d.get('disk_total_gb')} جيجابايت ({d.get('disk_used_pct')}% مستخدم)")
        lines.append(f"   التفاصيل: {loc.get('disk_detail', '')}")
        lines.append("")
        lines.append(f"5) Git (alforaijboard-gh): {'ملوث' if d.get('git_uncommitted') == 'unclean' else 'نظيف'}")
        lines.append(f"   التفاصيل: {loc.get('git_detail', '')}")
        lines.append("")
        lines.append("ملخص سريع:")
        lines.append(f"  Docker: {d.get('docker')}")
        lines.append(f"  الذاكرة: {'OK' if d.get('ram_ok') == 'yes' else 'LOW'} ({d.get('ram_free_mb')} ميجابايت حر)")
        lines.append(f"  العمليات: {'OK' if d.get('hermes_agents') else 'NOT_FOUND'}")
        lines.append(f"  القرص: {'WARN' if d.get('disk_warn') == 'yes' else 'OK'} ({d.get('disk_free_gb')} جيجابايت حر, {d.get('disk_used_pct')}% مستخدم)")
        lines.append(f"  Git: {d.get('git_uncommitted')} ({loc.get('git_detail', '')})")
        lines.append("")
        lines.append("3 مشاكل:")
        lines.append("  - Docker daemon متوقف")
        lines.append("  - مساحة القرص C: أقل من عتبة 10%")
        lines.append("  - Git repo فيه تغييرات غير مُ commits")
    else:
        lines.append(f"Health check report - {stamp} (Kuwait time)")
        lines.append("")
        lines.append(f"Overall: {loc.get('overall', 'UNKNOWN')} (3 issues)")
        lines.append("")
        lines.append(f"1) Docker: {d.get('docker')}")
        lines.append(f"   Detail: {loc.get('docker_detail', '')}")
        lines.append("")
        lines.append(f"2) RAM: {'OK' if d.get('ram_ok') == 'yes' else 'LOW'}")
        lines.append(f"   Free: {d.get('ram_free_mb')} MB / Total {d.get('ram_total_mb')} MB")
        lines.append(f"   Detail: {loc.get('ram_detail', '')}")
        lines.append("")
        lines.append(f"3) Hermes agents: {'OK' if d.get('hermes_agents') else 'NOT_FOUND'}")
        lines.append(f"   Detail: {d.get('hermes_agents')}")
        lines.append("")
        lines.append(f"4) Disk C:/Users/hello: {'WARN' if d.get('disk_warn') == 'yes' else 'OK'}")
        lines.append(f"   Free: {d.get('disk_free_gb')} GB / Total {d.get('disk_total_gb')} GB ({d.get('disk_used_pct')}% used)")
        lines.append(f"   Detail: {loc.get('disk_detail', '')}")
        lines.append("")
        lines.append(f"5) Git (alforaijboard-gh): {'UNCLEAN' if d.get('git_uncommitted') == 'unclean' else 'CLEAN'}")
        lines.append(f"   Detail: {loc.get('git_detail', '')}")
        lines.append("")
        lines.append("Quick summary:")
        lines.append(f"  Docker: {d.get('docker')}")
        lines.append(f"  RAM: {'OK' if d.get('ram_ok') == 'yes' else 'LOW'} ({d.get('ram_free_mb')} MB free)")
        lines.append(f"  Agents: {'OK' if d.get('hermes_agents') else 'NOT_FOUND'}")
        lines.append(f"  Disk: {'WARN' if d.get('disk_warn') == 'yes' else 'OK'} ({d.get('disk_free_gb')} GB free, {d.get('disk_used_pct')}% used)")
        lines.append(f"  Git: {d.get('git_uncommitted')} ({loc.get('git_detail', '')})")
        lines.append("")
        lines.append("3 issues:")
        lines.append("  - Docker daemon stopped")
        lines.append("  - Disk C: free space below 10% threshold")
        lines.append("  - Git repo has uncommitted changes")
    return "\n".join(lines)

if __name__ == "__main__":
    json_path = "_cron_health_latest.json"
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("--path="):
            json_path = arg.split("=", 1)[1]
        elif arg in ("--en", "--ar"):
            pass
        else:
            json_path = arg

    lang = "ar"
    for a in sys.argv[1:]:
        if a == "--en":
            lang = "en"
        elif a == "--ar":
            lang = "ar"

    d = load(json_path)
    text = build(d, lang)
    print(text)

    out_path = "_cron_health_latest.txt"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(build(d, "ar"))
            f.write("\n\n")
            f.write(build(d, "en"))
        print(f"\nSaved to: {out_path}")
    except Exception as e:
        print(f"\nCould not write file: {e}")
