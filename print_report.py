#!/usr/bin/env python3
"""Read latest health JSON and print 3-level Arabic report."""
import json, datetime, os, sys

RESULTS_DIR = "/c/Users/hello/alforaijboard-gh/cron_results"
HISTORY = "/c/Users/hello/alforaijboard-gh/cron_results_local.json"

def find_latest():
    files = sorted([f for f in os.listdir(RESULTS_DIR)
                    if f.startswith("cron_results_") and f.endswith(".json")
                    and not f.endswith(".synced")])
    if not files:
        if os.path.exists(HISTORY):
            with open(HISTORY) as f:
                data = json.load(f)
            if data:
                return data[-1]
        return None
    path = os.path.join(RESULTS_DIR, files[-1])
    with open(path) as f:
        return json.load(f)

report = find_latest()
if not report:
    print("No health data found"); sys.exit(1)

c = report.get("checks", {})
ram = c.get("ram", {})
disk = c.get("disk", {})
docker = c.get("docker", {})
git = c.get("git", {})
proc = c.get("processes", {})

ram_ok = ram.get("status") == "ok"
disk_ok = disk.get("status") == "ok"
docker_ok = docker.get("status") == "running"
git_ok = git.get("status") == "clean"
overall = "HEALTHY" if (ram_ok and disk_ok and docker_ok and git_ok) else "NEEDS_ATTENTION"

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
ts = now.strftime("%Y-%m-%d %H:%M KWT")

def pct(part, whole):
    try:
        return round(float(part) / float(whole) * 100, 1)
    except Exception:
        return "—"

# Level 1
l1 = f"""
########## تقرير الصحة الساعة {ts} ##########

STATUS: {overall}

🟢 الذاكرة: {ram.get('free_gb', '—')} غيغابايت حرّ من {ram.get('total_mb', '—')} ميجابايت كلها — {ram.get('status', '—').upper()}
{'🔴' if not docker_ok else '🟢'} دوكر: {docker.get('status', '—').upper()} — {'توقف' if not docker_ok else 'شغال'}
{'🟡' if not disk_ok else '🟢'} القرص: {disk.get('free_gb', '—')} غيغابايت فارغ من {disk.get('total_gb', '—')} — {disk.get('free_pct', '—')}% حرّ
{'🟡' if not git_ok else '🟢'} جيت: {git.get('status', '—').upper()} — {'فيها تعديلات' if not git_ok else 'نظيفة'}

"""

print(l1)

# Level 2
l2 = f"""
----- مستوى أوسع -----

1) دوكر:
   - الحالة: {docker.get('status', 'غير معروف')}
   - التفاصيل: {docker.get('output', '')[:250] or docker.get('details', '—')[:250]}
   - المعنى: {'Docker Desktop شغال' if docker_ok else 'مش وصل — ممكن توقف أو مقفل أو Windows نسيه'}

2) الذاكرة:
   - حرّ: {ram.get('free_mb', '—')} ميجابايت ({ram.get('free_gb', '—')} غيغابايت)
   - كلها: {ram.get('total_mb', '—')} ميجابايت
   - النسبة: {pct(ram.get('free_mb',0), ram.get('total_mb',1))}% حرّ
   - العتبة: 500 ميجابايت — {'تجاوز العتبة' if not ram_ok else 'آمن'}

3) العمليات (الحمل):
   - حمل المعالج: {proc.get('load_percent', '—')}%
   - ملاحظة: {proc.get('note', '—')}

4) القرص:
   - الكلي: {disk.get('total_gb', '—')}
   - المستعمل: {disk.get('used_gb', '—')}
   - الفارغ: {disk.get('free_gb', '—')} ({disk.get('free_pct', '—')}%)
   - العتبة: 10% — {'على حدّه أو أقل — خطر' if not disk_ok else 'آمن'}

5) جيت:
   - الحالة: {git.get('status', '—')}
   - المعدّل: {', '.join(git.get('modified', [])) if git.get('modified') else 'ما يوجد'}
   - غير المُراقَب: {', '.join(git.get('untracked', [])) if git.get('untracked') else 'ما يوجد'}
"""

print(l2)

# Level 3
l3 = f"""
----- مستوى المقترحات -----

أ) دوكر متوقف:
   - افتح Docker Desktop يدوياً من ابدأ أو شريط المهام.
   - لو كان شغال وقت بالمساء و subnets الصباح: شكو Windows Update أو restart.
   - لحل أوتوماتيكت كامل، ممكن أكتب task scheduler يفتح Docker لو "docker ps" فشل، أو Hermes cron ثاني بيقلّب وظيفة إيش.

ب) القرص على {disk.get('free_pct', '—')}% — حاول:
   - Disk Cleanup (cleanmgr) على C — ازل winsxs و temp و updating.
   - امسح ملفات cron_results القديمة غير .json (أو اللي .synced) لأنها مكررة.
   - لو في تحميلات كبيرة أو نسخ احتياطية على C، انقلهم لقرص ثاني.
   - لو حابب monitoring_continuous: أضف تنبيه إذا free_pct < 10%.

ج) جيت بهAdjustions:
   - لو التعديلات مقصودة: git add -A && git commit -m "update" && git push
   - لو ما في داعي: git stash (للمعدّل) + git clean -fd (لـ untracked)، لكن الحذر مع untracked مهم.
   - ملفات مثل _cron_health_latest.json و static-data/e2e-test-report.json ممكن تكون من اختبارات سابقة — ممكن تمسح أو تُضاف لـ .gitignore.

د) Supabase tracking:
   -olumn "details" في cron_results غير موجودة في schema (PGRST204 HTTP 400) — لازم نضيف column details JSONB قبل ما نرسل التفاصيل الكاملة.
   - الحल المؤقت: تخزين ملخص Columns فقط (docker_status، ram_free_mb، disk_free_pct، git_status) كما جرّبنا للمرة الجايبة.

ه) أوتomatisasi أقوى:
   - إشعار فوري إذا docker يتوقف (Email أو Teams أو webhook).
   - مراقبة disk thresholding مع time series عشان نعرف 추세 قبل ما يصير مشكلة.
"""

print(l3)
print(f"\nFINAL STATUS: {overall} — time: {ts}")
