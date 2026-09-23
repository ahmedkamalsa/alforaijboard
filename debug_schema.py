#!/usr/bin/env python3
"""Supabase REST introspection: table list, column list, row count for cron_results."""
import os, json, urllib.request, urllib.error
PROJECT = "bwspcsiazbwrrxpgoldx"
URL = f"https://{PROJECT}.supabase.co"

def get_key():
    k = os.environ.get("SUPABASE_ANON_KEY") or ""
    if k:
        return k
    dotenv = "/c/Users/hello/alforaijboard-gh/.env"
    if os.path.exists(dotenv):
        for line in open(dotenv, encoding="utf-8"):
            s = line.strip()
            if s.startswith("SUPABASE_ANON_KEY="):
                return s.split("=",1)[1].strip().strip('"').strip("'")
    return ""

key = get_key()
if not key:
    print("[SKIP] no key"); raise SystemExit(0)

HEADERS = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def get(path, params=None):
    q = "" if not params else "?" + "&".join(f"{k}={v}" for k,v in params.items())
    req = urllib.request.Request(URL + path + q, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, repr(e)

print("=== 1. Tables (exclude system) ===", flush=True)
code, data = get("/rest/v1/", {"select":"table_name", "tables_only":"true", "schema":"public"})
print(f"HTTP {code}", flush=True)
if isinstance(data, list):
    for t in data:
        print(f"  TABLE: {t}", flush=True)
elif isinstance(data, dict):
    print(f"  DATA: {json.dumps(data, ensure_ascii=False)[:500]}", flush=True)
else:
    print(f"  RAW: {str(data)[:500]}", flush=True)

print("\n=== 2. information_schema.columns for cron_results ===", flush=True)
code, cols = get("/rest/v1/information_schema/columns", {"table_schema":"public", "table_name":"cron_results"})
print(f"HTTP {code}", flush=True)
print(f"  {json.dumps(cols, ensure_ascii=False)[:1200]}", flush=True)

print("\n=== 3. Count cron_results rows ===", flush=True)
code, cnt = get("/rest/v1/cron_results", {"count":"true"})
print(f"HTTP {code}", flush=True)
print(f"  {json.dumps(cnt, ensure_ascii=False)[:300]}", flush=True)

print("\n=== 4. First row of cron_results (if any) ===", flush=True)
code, row = get("/rest/v1/cron_results", {"limit":"1"})
print(f"HTTP {code}", flush=True)
print(f"  {json.dumps(row, ensure_ascii=False)[:600]}", flush=True)
