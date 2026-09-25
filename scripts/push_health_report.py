import os, json, time, urllib.request, urllib.error

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://bwspcsiazbwrrxpgoldx.supabase.co")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Build report
docker_status = "DOWN"
docker_detail = "Daemon unreachable (npipe missing); restart failed — service cannot be opened"

ram_free_mb = 3303892 / 1024  # from wmic FreePhysicalMemory
ram_total_mb = 16653704 / 1024
ram_pct = (ram_total_mb - ram_free_mb) / ram_total_mb * 100
ram_status = "OK" if ram_free_mb > 500 else "LOW"

agents_count = 21
agents_status = "OK"

disk_total_gb = 196
disk_free_gb = 21
disk_free_pct = disk_free_gb / disk_total_gb * 100
disk_status = "OK" if disk_free_pct > 10 else ("LOW" if disk_free_pct > 5 else "CRITICAL")

git_dirty_count = 4  # modified
git_untracked_count = 17
git_status = "DIRTY"

alerts = []
if docker_status == "DOWN":
    alerts.append(f"[DOCKER] DOWN — {docker_detail}")
if git_status == "DIRTY":
    alerts.append(f"[GIT] DIRTY — {git_dirty_count} modified + {git_untracked_count} untracked files")

summary_line = (
    f"[DOCKER] {docker_status} — {docker_detail}\n"
    f"[RAM] {ram_status} — {ram_free_mb:.0f} MB free / {ram_total_mb:.0f} MB total ({ram_pct:.1f}% used)\n"
    f"[AGENTS] {agents_status} — {agents_count} Hermes-related process(es) found\n"
    f"[DISK C:] {disk_status} — {disk_free_gb} GB free ({disk_free_pct:.1f}%) / {disk_total_gb} GB total\n"
    f"[GIT] {git_status} — {git_dirty_count} modified + {git_untracked_count} untracked\n"
)

overall = "error" if alerts else "success"
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
report_id = f"health_check_{time.strftime('%Y%m%d_%H%M')}"

payload = json.dumps({
    "name": report_id,
    "status": overall,
    "message": summary_line + ("\n".join(f"! {a}" for a in alerts) if alerts else "All systems nominal."),
    "duration_ms": None,
    "records_affected": None,
}).encode("utf-8")

url = f"{SUPABASE_URL}/rest/v1/cron_results"
headers = {
    "Content-Type": "application/json",
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "return=minimal",
}

req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        print(f"HTTP {resp.status} — pushed to Supabase")
        print(f"Response: {body[:300]}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code} — {e.reason}")
    print(e.read().decode("utf-8")[:500])
except Exception as e:
    print(f"ERROR: {e}")
