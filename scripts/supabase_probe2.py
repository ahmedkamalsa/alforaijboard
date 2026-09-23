#!/usr/bin/env python3
"""Supabase probe — new key style (apikey header only)."""
import os, json, urllib.request

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ")

def get(path, headers, timeout=15):
    req = urllib.request.Request(URL + path, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode()

def post(path, headers, body, timeout=15):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(URL + path, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

print("=== SUPABASE PROBE (new key style) ===\n")

# 1. ANON/publishable key: apikey header only, NO auth header
anon_headers = {"apikey": ANON_KEY, "Content-Type": "application/json"}
try:
    st, body = get("/rest/v1/cron_results?limit=1", anon_headers)
    print(f"[ANON] GET cron_results (apikey only, no auth): HTTP {st}")
    print(f"  body: {body[:400]}\n")
except Exception as e:
    print(f"[ANON] GET FAILED: {e}\n")

if SERVICE_KEY:
    # 2. Service key: apikey header only, NO auth
    svc_headers = {"apikey": SERVICE_KEY, "Content-Type": "application/json"}
    try:
        st, body = get("/rest/v1/cron_results?limit=1", svc_headers)
        print(f"[SVC] GET cron_results (apikey only, no auth): HTTP {st}")
        print(f"  body: {body[:400]}\n")
    except Exception as e:
        print(f"[SVC] GET FAILED: {e}\n")
    
    # 3. Service key INSERT: apikey header only
    row = {
        "timestamp": "2026-09-22T04:30:00+00:00",
        "overall": "HEALTHY",
        "docker_status": "RUNNING",
        "ram_free_mb": 5000,
        "ram_status": "OK",
        "disk_free_pct": 15,
        "disk_status": "OK",
        "git_status": "CLEAN",
        "details": json.dumps({"docker":{"status":"RUNNING","severity":"info","details":"test"}}, ensure_ascii=False),
        "name": "cron_health_probe_v2",
        "status": "success",
        "message": "probe test v2",
    }
    st, body = post("/rest/v1/cron_results", svc_headers, row)
    print(f"[SVC] POST cron_results (apikey only, no auth): HTTP {st}")
    print(f"  body: {body[:400]}\n")
    
    # 4. Service key INSERT: apikey + verify_jwt=false
    st, body = post("/rest/v1/cron_results?disable+jwt=1", svc_headers, row)
    print(f"[SVC] POST cron_results (?disable+jwt=1, apikey only): HTTP {st}")
    print(f"  body: {body[:400]}\n")
    
    # 5. Service key GET with ?select=*
    st, body = get("/rest/v1/cron_results?select=id,name,status,created_at&limit=2", svc_headers)
    print(f"[SVC] GET cron_results (select limited): HTTP {st}")
    print(f"  body: {body[:400]}\n")
else:
    print("[SVC] No service key set — skipping service-key tests")

print("=== DONE ===")
