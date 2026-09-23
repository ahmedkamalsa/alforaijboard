#!/usr/bin/env python3
"""Append health check result to Supabase cron_results via REST API.

NOTE: This push writes to a table protected by RLS. If running
with only an anon key, the insert will be rejected (401). In that
case the result is still printed to stdout so the local caller can
persist it or log it independently.
"""
import os, json, urllib.request, urllib.error, datetime

env_path = "/c/Users/hello/alforaijboard-gh/.env"
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

url = os.environ.get("SUPABASE_URL", "").rstrip("/")
key = os.environ.get("SUPABASE_ANON_KEY", "")
table = "cron_results"

if not url or not key:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY")
    exit(1)

free_bytes = int(os.environ.get("FREE_MEM_KB", "0")) * 1024
total_bytes = int(os.environ.get("TOTAL_MEM_KB", "0")) * 1024
free_mb = free_bytes / (1024*1024)

timestamp = os.environ.get("RUN_AT", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

# Build a plain-text message summary
msg_parts = [
    f"Docker: {'RUNNING' if os.environ.get('DOCKER_RUNNING','false')=='true' else 'DOWN'}",
    f"RAM: {round(free_mb,1)}MB free / {round(total_bytes/(1024*1024),1)}MB (status: {os.environ.get('RAM_STATUS','?')})",
    f"Disk C: {os.environ.get('DISK_FREE_GB','?')}GB free / {os.environ.get('DISK_TOTAL_GB','?')}GB ({os.environ.get('DISK_STATUS','?')})",
    f"Git: {os.environ.get('GIT_CHANGED','0')} changed, {os.environ.get('GIT_UNTRACKED','0')} untracked ({os.environ.get('GIT_STATUS','?')})",
    f"Agents: {os.environ.get('AGENTS_STATUS','?')}",
]
if os.environ.get("DOCKER_ERROR"):
    msg_parts.append(f"ERR: {os.environ.get('DOCKER_ERROR')[:300]}")

data = {
    "name": f"health_{timestamp.replace(' ','_').replace(':','-')}",
    "status": "success" if (
        os.environ.get("DOCKER_RUNNING","false") == "true"
        and os.environ.get("RAM_STATUS","") != "CRITICAL"
        and os.environ.get("DISK_STATUS","") != "CRITICAL"
    ) else "warning",
    "message": " | ".join(msg_parts),
    "created_at": timestamp
}

payload = json.dumps(data).encode("utf-8")
req = urllib.request.Request(
    f"{url}/rest/v1/{table}",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Prefer": "return=minimal"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        print(f"OK: inserted row {result.get('id', '?')}")
except urllib.error.HTTPError as e:
    if e.code == 401:
        print(f"RLS blocks anon-key push (401) — result available for local persistence: {json.dumps(data)}")
    else:
        print(f"HTTP Error {e.code}: {e.read().decode()[:300]}")
except Exception as e:
    print(f"Error: {e}")
