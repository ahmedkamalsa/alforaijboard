#!/usr/bin/env python3
"""E2E Test for Dashboard"""
import json, os, urllib.request, ssl, sys
from datetime import datetime, timezone

PROJECT_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
DASHBOARD_URL = "https://ahmedkamalsa.github.io/alforaijboard/"
BASE_DIR = os.getcwd()
HEALTH_JSON = os.path.join(BASE_DIR, "site", "static-data", "health.json")
E2E_REPORT = os.path.join(BASE_DIR, "site", "static-data", "e2e-test-report.json")

def ensure_dir(path):
    d = os.path.dirname(path)
    if not os.path.exists(d): os.makedirs(d, exist_ok=True)
    return d

def test_api():
    print("1. Testing Supabase API...") 
    ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    BASE = PROJECT_URL + "/rest/v1"
    try:
        req = urllib.request.Request(BASE + "/market_listings?select=count&id&limit=1")
        req.add_header("apikey", ANON_KEY)
        req.add_header("Authorization", "Bearer " + ANON_KEY)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = json.loads(resp.read())
            count = data[0]["count"] if data else 0
            print("   API: " + str(count) + " listings")
            return count
    except Exception as e:
        print("   API: " + str(e))
        return 0

def test_dashboard():
    print("2. Testing Dashboard...") 
    try:
        req = urllib.request.Request(DASHBOARD_URL)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            print("   Dashboard: HTTP " + str(resp.status) + ", " + str(len(content)) + " bytes")
            return resp.status == 200
    except Exception as e:
        print("   Dashboard: " + str(e))
        return False

def test_health():
    print("3. Testing health.json...") 
    try:
        ensure_dir(HEALTH_JSON)
        with open(HEALTH_JSON, "r") as f:
            health = json.load(f)
            status = health.get("status", "unknown")
            print("   health.json: status = " + status)
            return status == "connected_live"
    except Exception as e:
        print("   health.json: " + str(e))
        return False

def test_sources():
    print("4. Testing source_stats...") 
    ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    BASE = PROJECT_URL + "/rest/v1"
    try:
        req = urllib.request.Request(BASE + "/source_stats?order=listings_count.desc&limit=10")
        req.add_header("apikey", ANON_KEY)
        req.add_header("Authorization", "Bearer " + ANON_KEY)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            stats = json.loads(resp.read())
            print("   source_stats: " + str(len(stats)) + " sources")
            for s in stats[:3]:
                print("      - " + str(s.get("listings_count", 0)) + " listings")
            return len(stats)
    except Exception as e:
        print("   source_stats: " + str(e))
        return 0

def main():
    print("=== E2E Test | " + datetime.now().isoformat()[:19] + " ===") 
    results = {
        "api_count": test_api(),
        "dashboard_ok": test_dashboard(),
        "health_ok": test_health(),
        "source_count": test_sources(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    print("") 
    print("=" * 60)
    print("Final Results:")
    if results["api_count"] > 0: print("  API: " + str(results["api_count"]) + " listings")
    else: print("  API: no data")
    print("  Dashboard: OK" if results["dashboard_ok"] else "  Dashboard: unreachable")
    print("  Health: connected_live" if results["health_ok"] else "  Health: not connected")
    if results["source_count"] > 0: print("  Sources: " + str(results["source_count"]) + " sources")
    else: print("  Sources: no data")
    all_ok = all([results["api_count"] > 0, results["dashboard_ok"], results["health_ok"], results["source_count"] > 0])
    print("") 
    print("ALL TESTS PASSED" if all_ok else "SOME TESTS FAILED")
    print("Timestamp: " + results["timestamp"])
    ensure_dir(E2E_REPORT)
    with open(E2E_REPORT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Report saved: " + E2E_REPORT)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
