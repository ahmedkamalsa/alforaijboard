#!/usr/bin/env python3
"""Test insert with ONLY columns confirmed to exist in cron_results."""
import os, json, urllib.request, subprocess

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "sb_secret_dekuatGb5ZKi8FD5ku2PfAfGM2DSqxNvN8DjT0uMQqo")
ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"
HOST = "bwspcsiazbwrrxpgoldx.supabase.co"
API_URL = f"https://{HOST}/rest/v1/cron_results"

def try_post(key_label, api_key, row, extra_headers=None):
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            print(f"  [{key_label}] HTTP {resp.status} — {body[:300]}")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [{key_label}] HTTP {e.code} — {body[:300]}")
        return e.code, body
    except Exception as e:
        print(f"  [{key_label}] ERROR — {e}")
        return -1, str(e)

print("=== SUPABASE INSERT WITH MINIMAL KNOWN COLUMNS ===\n")

# These columns exist (confirmed by earlier GET returning them):
# id, name, status, message, duration_ms, records_affected, created_at
# Also returned by GET: timestamp, overall, docker_status, ram_free_mb, ram_status,
#   disk_free_pct, disk_status, git_status, details
# PGRST204 says disk_free_pct is NOT in schema cache.
# Known-good columns from first successful GET row:
#   id, name, status, message, duration_ms, records_affected, created_at
KNOWN_COLUMNS = ["timestamp", "name", "status", "message", "duration_ms", "records_affected"]

row = {col: ("test_value" if col in ("message", "name") else "2026-09-22T04:34:00+00:00" if col == "timestamp" else 123 if col == "duration_ms" else None) for col in KNOWN_COLUMNS}
row["name"] = "probe_known_cols"
row["status"] = "success"
row["message"] = "test with known columns only"
row["timestamp"] = "2026-09-22T04:34:00+00:00"
row["duration_ms"] = 500
row["records_affected"] = None

# Test 1: ANON key, known columns only
print("--- Test 1: ANON key, known columns only ---")
try_post("ANON", ANON_KEY, row)

# Test 2: SERVICE key, known columns only
print("\n--- Test 2: SERVICE key, known columns only ---")
try_post("SERVICE", SERVICE_KEY, row)

# Test 3: Service key + Authorization Bearer
print("\n--- Test 3: SERVICE key + Authorization Bearer, known columns only ---")
try_post("SVC+AUTH", SERVICE_KEY, row, extra_headers={"Authorization": f"Bearer {SERVICE_KEY}"})

# Test 4: curl
print("\n--- curl: SERVICE key, apikey only, known columns ---")
proc = subprocess.run(
    ["curl", "-s", "-w", "\n%{http_code}", "-X", "POST", API_URL,
     "-H", f"apikey: {SERVICE_KEY}",
     "-H", "Content-Type: application/json",
     "-d", json.dumps(row)],
    capture_output=True, text=True, timeout=10)
print(f"  curl exit: {proc.returncode}")
print(f"  output:\n{proc.stdout}")
if proc.stderr:
    print(f"  stderr: {proc.stderr}")

# Test 5: Try with ALL columns we think exist (including the ones from GET)
print("\n--- Test 5: ANON key, full row with all GET-returned columns ---")
full_row = {
    "timestamp": "2026-09-22T04:34:00+00:00",
    "name": "probe_full_row",
    "status": "success",
    "message": "test full row",
    "duration_ms": 500,
    "records_affected": None,
    "created_at": "2026-09-22T04:34:00+00:00",
    "overall": "HEALTHY",
    "docker_status": "RUNNING",
    "ram_free_mb": 5000,
    "ram_status": "OK",
    "disk_free_pct": 15.0,
    "disk_status": "OK",
    "git_status": "CLEAN",
    "details": json.dumps({"docker":{"status":"RUNNING","severity":"info","details":"test"}}, ensure_ascii=False),
}
try_post("ANON-FULL", ANON_KEY, full_row)

print("\n=== DONE ===")
