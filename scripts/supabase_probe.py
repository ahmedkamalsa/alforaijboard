#!/usr/bin/env python3
"""Supabase schema probe for cron_results table."""
import os, json, urllib.request

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
if not ANON_KEY:
    ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"

def gen_headers(api_key, auth_bearer):
    return {"apikey": api_key, "Authorization": f"Bearer {auth_bearer}", "Content-Type": "application/json"}

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

print("=== SUPABASE SCHEMA PROBE ===")

# 1. ANON key access
anon_headers = gen_headers(ANON_KEY, ANON_KEY)
try:
    st, body = get("/rest/v1/cron_results?limit=1", anon_headers)
    print(f"[ANON] GET cron_results (apikey={ANON_KEY[:8]}…, auth=same): HTTP {st}")
    print(f"  body: {body[:300]}")
except Exception as e:
    print(f"[ANON] GET cron_results FAILED: {e}")

# 1b. ANON key with auth=service_key (should still fail RLS for INSERT)
try:
    st, body = get("/rest/v1/cron_results?limit=1", gen_headers(ANON_KEY, SERVICE_KEY if SERVICE_KEY else ANON_KEY))
    print(f"[ANON] GET cron_results (apikey=anon, auth=svc): HTTP {st}")
    print(f"  body: {body[:200]}")
except Exception as e:
    print(f"[ANON] GET cron_results (anon apikey + svc auth) FAILED: {e}")

# 2. Service key access
if SERVICE_KEY:
    svc_headers = gen_headers(SERVICE_KEY, SERVICE_KEY)
    try:
        st, body = get("/rest/v1/cron_results?limit=1", svc_headers)
        print(f"[SVC] GET cron_results (apikey=svc, auth=svc): HTTP {st}")
        print(f"  body: {body[:300]}")
    except Exception as e:
        print(f"[SVC] GET cron_results FAILED: {e}")
    
    # 3. Try INSERT with service key
    row = {
        "timestamp": "2026-09-22T04:27:00+00:00",
        "overall": "HEALTHY",
        "docker_status": "RUNNING",
        "ram_free_mb": 5000,
        "ram_status": "OK",
        "disk_free_pct": 15,
        "disk_status": "OK",
        "git_status": "CLEAN",
        "details": json.dumps({"docker":{"status":"RUNNING","severity":"info","details":"test"}}, ensure_ascii=False),
        "name": "cron_health_probe",
        "status": "success",
        "message": "probe test",
    }
    st, body = post("/rest/v1/cron_results", svc_headers, row)
    print(f"[SVC] POST cron_results (apikey=svc, auth=svc): HTTP {st}")
    print(f"  body: {body[:300]}")
    
    # 4. Try anon apikey + svc auth (hybrid)
    hybrid_headers = gen_headers(ANON_KEY, SERVICE_KEY)
    st, body = post("/rest/v1/cron_results", hybrid_headers, row)
    print(f"[HYBRID] POST cron_results (apikey=anon, auth=svc): HTTP {st}")
    print(f"  body: {body[:300]}")
else:
    print("[SVC] No service key set — skipping service-key tests")

# 5. Try URL query param apikey
if SERVICE_KEY:
    try:
        st, body = get(f"/rest/v1/cron_results?limit=1&apikey={SERVICE_KEY}", gen_headers("", SERVICE_KEY))
        print(f"[URL] GET cron_results (apikey=svc in URL, auth=svc): HTTP {st}")
        print(f"  body: {body[:200]}")
    except Exception as e:
        print(f"[URL] FAILED: {e}")

print("\n=== DONE ===")
