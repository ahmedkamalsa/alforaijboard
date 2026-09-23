#!/usr/bin/env python3
"""Test Supabase REST with minimal row (no problematic columns)."""
import os, json, urllib.request, subprocess

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "sb_secret_dekuatGb5ZKi8FD5ku2PfAfGM2DSqxNvN8DjT0uMQqo")
ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"
HOST = "bwspcsiazbwrrxpgoldx.supabase.co"

def try_post(key_label, api_key, extra_headers=None, row=None):
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if row is None:
        row = {"timestamp": "2026-09-22T04:33:00+00:00", "overall": "HEALTHY",
               "docker_status": "RUNNING", "ram_free_mb": 5000, "ram_status": "OK",
               "disk_free_pct": 15, "disk_status": "OK", "git_status": "CLEAN",
               "name": f"probe_{key_label}", "status": "success", "message": f"test {key_label}"}
    data = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(f"https://{HOST}/rest/v1/cron_results", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            print(f"  [{key_label}] HTTP {resp.status} — {body[:200]}")
    except urllib.error.HTTPError as e:
        print(f"  [{key_label}] HTTP {e.code} — {e.read().decode()[:250]}")
    except Exception as e:
        print(f"  [{key_label}] ERROR — {e}")

print("=== SUPABASE INSERT TEST (minimal row) ===\n")

# Test 1: ANON key, minimal row (no details column)
try_post("ANON", ANON_KEY)

# Test 2: SERVICE key, minimal row
try_post("SERVICE", SERVICE_KEY)

# Test 3: SERVICE key + Authorization Bearer (legacy style)
try_post("SERVICE+AUTH", SERVICE_KEY, extra_headers={"Authorization": f"Bearer {SERVICE_KEY}"})

# Test 4: curl — service key, minimal row
print("\n=== curl test (SERVICE key, apikey header) ===")
row4 = {"timestamp": "2026-09-22T04:33:00+00:00", "overall": "HEALTHY",
        "docker_status": "RUNNING", "ram_free_mb": 5000, "ram_status": "OK",
        "disk_free_pct": 15, "disk_status": "OK", "git_status": "CLEAN",
        "name": "probe_curl", "status": "success", "message": "curl test"}
proc = subprocess.run(
    ["curl", "-s", "-w", "\n%{http_code}", "-X", "POST",
     f"https://{HOST}/rest/v1/cron_results",
     "-H", f"apikey: {SERVICE_KEY}",
     "-H", "Content-Type: application/json",
     "-d", json.dumps(row4)],
    capture_output=True, text=True, timeout=10)
print(f"  curl exit: {proc.returncode}")
print(f"  output:\n{proc.stdout}")
if proc.stderr:
    print(f"  stderr: {proc.stderr}")

print("\n=== DONE ===")
