#!/usr/bin/env python3
"""Supabase management API probe — tables, schema, health (uses service_role key if available)."""
import os, json, urllib.request, urllib.error
PROJECT = "bwspcsiazbwrrxpgoldx"
URL = f"https://{PROJECT}.supabase.co"

def get_key(tag):
    # try env, then .env, then scripts/key_test.py extraction (fallback)
    k = os.environ.get(tag) or ""
    if k:
        return k
    dotenv = "/c/Users/hello/alforaijboard-gh/.env"
    if os.path.exists(dotenv):
        for line in open(dotenv, encoding="utf-8"):
            s = line.strip()
            if s.startswith(f"{tag}="):
                return s.split("=",1)[1].strip().strip('"').strip("'")
    return ""

def mgmt_req(method, path, body=None, token=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, repr(e)

print("=== SUPABASE MGMT API PROBE ===", flush=True)

# Try service_role key first (full admin), then anon
for tag, label in [("SUPABASE_SERVICE_ROLE_KEY", "service_role"), ("SUPABASE_ANON_KEY", "anon")]:
    token = get_key(tag)
    print(f"\n--- Using {label} (tag={tag}) ---", flush=True)
    if not token:
        print("  [SKIP] key not available", flush=True)
        continue
    
    # Health
    code, body = mgmt_req("GET", "/health")
    print(f"  /health -> HTTP {code}: {json.dumps(body, ensure_ascii=False)[:200]}", flush=True)
    
    # List tables (admin only)
    if label == "service_role":
        code, tables = mgmt_req("GET", "/rest/v1/tables")
        print(f"  /rest/v1/tables -> HTTP {code}", flush=True)
        if isinstance(tables, list):
            for t in tables[:20]:
                print(f"    TABLE: {t}", flush=True)
        elif isinstance(tables, dict):
            print(f"    BODY: {json.dumps(tables, ensure_ascii=False)[:500]}", flush=True)
        else:
            print(f"    RAW: {str(tables)[:300]}", flush=True)
        
        if any(t.get("name")=="cron_results" for t in (tables if isinstance(tables,list) else [])):
            code, schema = mgmt_req("GET", "/rest/v1/tables/cron_results/columns")
            print(f"  /rest/v1/tables/cron_results/columns -> HTTP {code}", flush=True)
            print(f"    {json.dumps(schema, ensure_ascii=False)[:800]}", flush=True)
    else:
        print("  (admin table listing requires service_role key)", flush=True)

print("\n=== DONE ===", flush=True)
