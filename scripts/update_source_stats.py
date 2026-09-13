#!/usr/bin/env python3
"""Update source statistics in Supabase"""
import json, os, sys, urllib.request, ssl
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
SVC_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

def api_post(path, data, key=SVC_KEY):
    url = SUPABASE_URL + "/rest/v1" + path
    headers = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json", "Prefer": "return=minimal"}
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15) as resp:
            return json.loads(resp.read()), resp.status
    except Exception as e:
        return {"error": str(e)}, 0

def api_delete(path, key=SVC_KEY):
    url = SUPABASE_URL + "/rest/v1" + path
    headers = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"}
    req = urllib.request.Request(url, method="DELETE", headers=headers)
    try:
        urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15)
        return True, 200
    except: return False, 0

def main():
    print("Updating source_stats...") 
    ok, st = api_delete("/source_stats?limit=1000")
    print("  Delete old: " + ("OK" if ok else "Failed"))
    if not SVC_KEY:
        print("  No service key - skipping write")
        return 1
    try:
        url = SUPABASE_URL + "/rest/v1/sources?select=id,name,url&order=name.asc"
        headers = {"apikey": SVC_KEY, "Authorization": "Bearer " + SVC_KEY, "Content-Type": "application/json"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15) as resp:
            sources = json.loads(resp.read())
    except:
        print("Cannot fetch sources")
        return 1
    print("  Found " + str(len(sources)) + " sources")
    for src in sources:
        src_id = src["id"]
        src_name = src.get("name", "N/A")[:50]
        try:
            url = SUPABASE_URL + "/rest/v1/market_listings?select=count&id&source=eq."" + src_name + ""&limit=1"
            headers = {"apikey": SVC_KEY, "Authorization": "Bearer " + SVC_KEY, "Content-Type": "application/json"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15) as resp:
                data = json.loads(resp.read())
                count = data[0]["count"] if data else 0
        except:
            count = 0
        payload = {"source_id": src_id, "listings_count": count, "last_checked": datetime.now(timezone.utc).isoformat(), "reliability": 1, "error_count": 0}
        result, st = api_post("/source_stats", payload)
        if st == 201:
            print("  " + src_name + ": " + str(count) + " listings")
        else:
            print("  " + src_name + ": " + str(result.get("error", "failed")))
    print("Done")
    return 0

if __name__ == "__main__":
    sys.exit(main())
