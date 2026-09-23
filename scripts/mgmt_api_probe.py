#!/usr/bin/env python3
"""Management API probe: list API keys for project."""
import os, json, urllib.request

API_TOKEN = os.environ.get("SUPABASE_API_TOKEN", "")
if not API_TOKEN:
    API_TOKEN = "sbp_fc_placeholder_dummy_token_do_not_use"
    print("WARNING: No SUPABASE_API_TOKEN set. Using dummy placeholder — all calls will 401.")
    print("Set SUPABASE_API_TOKEN to a real personal access token from https://supabase.com/dashboard/account/tokens")
    print("Token needs: secrets:read (or full access)")
    print("")
URL = "https://api.supabase.com"

def get(path, headers, timeout=15):
    req = urllib.request.Request(URL + path, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode()

print("=== SUPABASE MANAGEMENT API PROBE ===\n")

if not API_TOKEN:
    print("No SUPABASE_API_TOKEN set — skipping.")
    print("To get keys, set SUPABASE_API_TOKEN=paste_personal_access_token_here")
    print("Token needs scope: secrets:read")
    print("Create at: https://supabase.com/dashboard/account/tokens")
    print("\n=== DONE ===")
    exit(0)

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "Prefer": "wait=0",
}

# 1. List projects (to confirm token works)
try:
    st, body = get("/v1/projects", headers)
    print(f"[MGMT] GET /v1/projects: HTTP {st}")
    projects = json.loads(body)
    print(f"  Found {len(projects)} project(s)")
    for p in projects[:5]:
        print(f"    - {p.get('name')} ({p.get('ref')})")
except Exception as e:
    print(f"[MGMT] GET /v1/projects FAILED: {e}")

# 2. Get API keys for bwspcsiazbwrrxpgoldx
try:
    st, body = get("/v1/projects/bwspcsiazbwrrxpgoldx/api-keys?reveal=true", headers)
    print(f"\n[MGMT] GET /v1/projects/bwspcsiazbwrrxpgoldx/api-keys?reveal=true: HTTP {st}")
    keys = json.loads(body)
    print(f"  Found {len(keys)} key(s):")
    for k in keys:
        print(f"    - name={k.get('name')} type={k.get('type')} prefix={k.get('prefix','?')[:8]}...")
        api_key = k.get('api_key', '')
        if api_key:
            print(f"      api_key: {api_key}")
except Exception as e:
    print(f"\n[MGMT] GET api-keys FAILED: {e}")

print("\n=== DONE ===")
