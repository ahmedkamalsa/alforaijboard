#!/usr/bin/env python3
"""Test Supabase REST with ngrok-style direct TCP to rule out key issues."""
import os, json, urllib.request, socket, ssl

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "sb_secret_dekuatGb5ZKi8FD5ku2PfAfGM2DSqxNvN8DjT0uMQqo")
ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"
HOST = "bwspcsiazbwrrxpgoldx.supabase.co"
PORT = 443

def try_http(keys_to_test, label):
    print(f"\n=== {label} ===")
    for key_label, api_key in keys_to_test:
        headers = {"apikey": api_key, "Content-Type": "application/json"}
        row = {"timestamp": "2026-09-22T04:32:00+00:00", "overall": "HEALTHY",
               "docker_status": "RUNNING", "ram_free_mb": 5000, "ram_status": "OK",
               "disk_free_pct": 15, "disk_status": "OK", "git_status": "CLEAN",
               "details": json.dumps({"docker":{"status":"RUNNING"}}, ensure_ascii=False),
               "name": f"probe_{key_label}", "status": "success", "message": f"test {key_label}"}
        data = json.dumps(row).encode("utf-8")
        req = urllib.request.Request(f"https://{HOST}/rest/v1/cron_results", data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode()
                print(f"  [{key_label}] HTTP {resp.status} — {body[:200]}")
        except urllib.error.HTTPError as e:
            print(f"  [{key_label}] HTTP {e.code} — {e.read().decode()[:200]}")
        except Exception as e:
            print(f"  [{key_label}] ERROR — {e}")

print("=== SUPABASE KEY COMPATIBILITY TEST ===\n")

# Test 1: anon key only
try_http([("ANON", ANON_KEY)], "Test 1: ANON key (apikey only)")

# Test 2: service key only
try_http([("SERVICE", SERVICE_KEY)], "Test 2: SERVICE key (apikey only)")

# Test 3: service key + Authorization header (legacy style)
headers3 = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}
row3 = {"timestamp": "2026-09-22T04:32:00+00:00", "overall": "HEALTHY",
        "docker_status": "RUNNING", "ram_free_mb": 5000, "ram_status": "OK",
        "disk_free_pct": 15, "disk_status": "OK", "git_status": "CLEAN",
        "details": json.dumps({"docker":{"status":"RUNNING"}}, ensure_ascii=False),
        "name": "probe_svc_auth", "status": "success", "message": "test svc+auth"}
data3 = json.dumps(row3).encode("utf-8")
req3 = urllib.request.Request(f"https://{HOST}/rest/v1/cron_results", data=data3, headers=headers3, method="POST")
try:
    with urllib.request.urlopen(req3, timeout=10) as resp:
        print(f"\n=== Test 3: SERVICE key + Authorization Bearer ===\n  HTTP {resp.status} — {resp.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"\n=== Test 3: SERVICE key + Authorization Bearer ===\n  HTTP {e.code} — {e.read().decode()[:200]}")
except Exception as e:
    print(f"\n=== Test 3: SERVICE key + Authorization Bearer ===\n  ERROR — {e}")

# Test 4: curl equivalent
print("\n=== Test 4: curl equivalent (service key, apikey only) ===")
import subprocess
proc = subprocess.run(
    ["curl", "-s", "-w", "\n%{http_code}", "-X", "POST",
     f"https://{HOST}/rest/v1/cron_results",
     "-H", f"apikey: {SERVICE_KEY}",
     "-H", "Content-Type: application/json",
     "-d", json.dumps(row3)],
    capture_output=True, text=True, timeout=10)
print(f"  curl exit: {proc.returncode}")
print(f"  stdout: {proc.stdout}")
if proc.stderr:
    print(f"  stderr: {proc.stderr}")

print("\n=== DONE ===")
