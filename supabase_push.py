import os, json, datetime, requests

env_path = "/c/Users/hello/alforaijboard-gh/.env"
if not os.path.exists(env_path):
    print("NO .env — skipping Supabase insert"); raise SystemExit(0)

# read .env manually (no exec)
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

url = env_vars.get("SUPABASE_URL", "").rstrip("/")
service_key = env_vars.get("SUPABASE_SERVICE_KEY", "")
anon_key = env_vars.get("SUPABASE_ANON_KEY", "")

# pick result file (latest cron_results)
results_dir = "/c/Users/hello/alforaijboard-gh/cron_results"
files = sorted([f for f in os.listdir(results_dir) if f.startswith("cron_results_") and f.endswith(".json") and not f.endswith(".synced")])
if not files:
    print("No cron_results JSON found"); raise SystemExit(0)

latest = files[-1]
path = os.path.join(results_dir, latest)
with open(path) as f:
    report = json.load(f)

# Build row
row = {
    "timestamp": report["timestamp"],
    "overall": report["overall"],
    "docker_status": report["checks"]["docker"]["status"],
    "ram_free_mb": report["checks"]["ram"]["free_mb"],
    "ram_status": report["checks"]["ram"]["status"],
    "disk_free_pct": report["checks"]["disk"].get("free_pct", 0),
    "disk_status": report["checks"]["disk"].get("status", "unknown"),
    "git_status": report["checks"]["git"]["status"],
    "details": json.dumps(report["checks"], ensure_ascii=False)
}

api_url = f"{url}/rest/v1/cron_results"
headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
try:
    r = requests.post(api_url, headers=headers, json=row, timeout=15)
    print(f"Supabase: HTTP {r.status_code} — {r.text[:300]}")
except Exception as e:
    print(f"Supabase insert failed: {e}")
