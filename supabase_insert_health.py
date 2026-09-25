import os, json, datetime, urllib.request, sys

key = os.environ.get('SUPABASE_ANON_KEY', '')
url = os.environ.get('SUPABASE_URL', '')
if not key or not url:
    print('NO_SUPABASE_ENV')
    sys.exit(0)

now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
row = {
    "timestamp": now,
    "docker_running": False,
    "containers": 0,
    "ram_free_mb": 2388,
    "ram_ok": True,
    "agent_processes": 34,
    "disk_free_pct": 11.0,
    "disk_ok": True,
    "git_clean": False,
    "git_changes": 5,
    "alerts": ["Docker daemon NOT running", "Git alforaijboard has uncommitted changes"],
    "report": "HEALTH CHECK - %s" % now,
}
data = json.dumps(row).encode()
req = urllib.request.Request(
    url + "/rest/v1/cron_results",
    data=data,
    method="POST",
    headers={
        "apikey": key,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    },
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    body = resp.read()
    print("INSERT_OK:", resp.status, body[:300])
except urllib.error.HTTPError as e:
    print("INSERT_HTTP_FAIL:", e.code, e.read()[:300])
except Exception as e:
    print("INSERT_FAIL:", type(e).__name__, str(e)[:300])
