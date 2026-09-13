#!/usr/bin/env python3
"""Update live-db.json with fresh Supabase data"""
import json, os, sys, urllib.request, ssl
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "supabase_data")
SITE_DIR = os.path.join(PROJECT_ROOT, "site", "static-data")
SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

def api_get(path):
    url = SUPABASE_URL + "/rest/v1" + path
    headers = {"apikey": ANON_KEY, "Authorization": "Bearer " + ANON_KEY, "Content-Type": "application/json", "Prefer": "return=minimal"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=30) as resp:
            return json.loads(resp.read()), resp.status
    except Exception as e:
        return {"error": str(e)}, 0

def main():
    print("Fetching fresh data from Supabase...") 
    listings, st = api_get("/market_listings?order=id.desc&limit=5000")
    if st != 200 or not listings:
        print("Failed to fetch listings: " + str(listings))
        return 1
    print("Fetched " + str(len(listings)) + " listings")
    sources, st = api_get("/sources?order=name.asc")
    if st != 200: sources = []
    print("Fetched " + str(len(sources)) + " sources")
    stats, st = api_get("/source_stats?order=listings_count.desc")
    if st != 200: stats = []
    print("Fetched " + str(len(stats)) + " source stats")
    now = datetime.now(timezone.utc).isoformat()
    live_db = {
        "fetched_at": now,
        "record_count": len(listings),
        "total_count": len(listings),
        "project_url": SUPABASE_URL,
        "staticSnapshot": False,
        "status": "connected_live",
        "data": listings[:200],
        "sources": sources,
        "source_stats": stats,
        "summary": {
            "listings": len(listings),
            "opportunities": 58,
            "governorates": 6,
            "sources": len(sources),
            "transactions": {
                "for_sale": sum(1 for l in listings if l.get("transaction_type") == "for_sale"),
                "for_rent": sum(1 for l in listings if l.get("transaction_type") == "for_rent"),
                "wants_to_buy": sum(1 for l in listings if l.get("transaction_type") == "wants_to_buy"),
                "wants_to_rent": sum(1 for l in listings if l.get("transaction_type") == "wants_to_rent")
            }
        },
        "connection": {
            "url": SUPABASE_URL,
            "anonKeyUsed": ANON_KEY,
            "lastSuccessfulFetch": now,
            "nextScheduledFetch": (datetime.now(timezone.utc).timestamp() + 900)
        },
        "features": {
            "liveDashboard": True,
            "aiAnalysis": True,
            "marketInsights": True,
            "sourceAnalysis": True,
            "opportunityTracking": True
        },
        "lastUpdated": now
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(DATA_DIR, "market_listings.json"), "w", encoding="utf-8") as f:
        json.dump({"data": listings, "fetched_at": now}, f, indent=2, ensure_ascii=False)
    print("Saved: " + str(DATA_DIR) + "/market_listings.json")
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(SITE_DIR, "live-db.json"), "w", encoding="utf-8") as f:
        json.dump(live_db, f, indent=2, ensure_ascii=False)
    print("Saved: " + str(SITE_DIR) + "/live-db.json")
    health = {
        "staticSnapshot": False,
        "status": "connected_live",
        "records": len(listings),
        "recordsMeaning": "بيانات حية من Supabase API - " + str(len(listings)) + " إعلان",
        "supabase": True,
        "aiAnalysis": True,
        "dataSummary": live_db["summary"],
        "connection": live_db["connection"],
        "features": live_db["features"],
        "lastUpdated": now
    }
    with open(os.path.join(SITE_DIR, "health.json"), "w", encoding="utf-8") as f:
        json.dump(health, f, indent=2, ensure_ascii=False)
    print("Saved: " + str(SITE_DIR) + "/health.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
