#!/usr/bin/env python3
"""
Incremental Supabase sync — fetches only new/changed listings.
Reduces egress by ~80-95% compared to fetching all 3,376 listings every 30 min.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co"
ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "supabase_data")
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_last_sync_time():
    """Get last successful sync timestamp from marker file."""
    marker_path = os.path.join(OUT_DIR, "last_sync_marker.json")
    if os.path.exists(marker_path):
        try:
            with open(marker_path, "r") as f:
                data = json.load(f)
                return data.get("last_sync_utc")
        except Exception:
            pass
    return None


def save_sync_marker(latest_timestamp):
    """Save the latest timestamp as the new sync marker."""
    marker_path = os.path.join(OUT_DIR, "last_sync_marker.json")
    with open(marker_path, "w") as f:
        json.dump({
            "last_sync_utc": latest_timestamp,
            "synced_at": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)


def fetch_incremental_listings():
    """
    Fetch only listings updated after last sync.
    Falls back to full fetch if no marker exists.
    """
    last_sync = get_last_sync_time()
    all_rows = []

    if last_sync:
        print(f"[INCREMENTAL] Last sync: {last_sync}")
        print("[INCREMENTAL] Fetching only changed listings...")
        last_sync_clean = last_sync.replace(' ', 'T')
        # Supabase REST API: update_at filter expects ISO 8601 with space not T
        url = f"{SUPABASE_URL}/rest/v1/market_listings?select=*&updated_at=gt.{last_sync}&order=updated_at.asc&limit=500"
        offset = 0
        limit = 500
        while True:
            fetch_url = f"{SUPABASE_URL}/rest/v1/market_listings?select=*&updated_at=gt.{last_sync}&limit={limit}&offset={offset}"
            try:
                data = fetch(fetch_url)
            except Exception as e:
                print(f"ERROR at offset {offset}: {e}")
                break
            if not data:
                break
            all_rows.extend(data)
            print(f"  Fetched {len(data)} rows (offset {offset}, total {len(all_rows)})")
            offset += limit
            if len(data) < limit:
                break
    else:
        print("[INCREMENTAL] No marker found — doing full initial fetch")
        offset = 0
        limit = 1000
        while True:
            fetch_url = f"{SUPABASE_URL}/rest/v1/market_listings?select=*&order=id.asc&limit={limit}&offset={offset}"
            try:
                data = fetch(fetch_url)
            except Exception as e:
                print(f"ERROR at offset {offset}: {e}")
                break
            if not data:
                break
            all_rows.extend(data)
            print(f"  Fetched {len(data)} rows (offset {offset}, total {len(all_rows)})")
            offset += limit
            if len(data) < limit:
                break

    return all_rows


def fetch_developments():
    """Fetch market developments with correct select clause."""
    url = f"{SUPABASE_URL}/rest/v1/market_developments?select=id,title,description,created_at,updated_at&orderby=id.desc&limit=200"
    try:
        data = fetch(url)
        return data if isinstance(data, list) else []
    except Exception as e:
        # Try without select to see if table exists at all
        print(f"  Retrying without select filter...")
        try:
            url2 = f"{SUPABASE_URL}/rest/v1/market_developments?orderby=id.desc&limit=200"
            data = fetch(url2)
            return data if isinstance(data, list) else []
        except Exception as e2:
            print(f"  ERROR: market_developments not accessible: {e2}")
            return []


def compute_statistics(listings):
    """Compute statistics from listings data."""
    source_counts = {}
    gov_set = set()
    area_set = set()
    price_vals = []
    price_undisclosed = 0

    for row in listings:
        src = row.get("source") or row.get("source_name") or "Unknown"
        source_counts[src] = source_counts.get(src, 0) + 1

        gov = row.get("governorate") or row.get("gov") or ""
        if gov:
            gov_set.add(gov)
        area = row.get("area") or row.get("area_name") or ""
        if area:
            area_set.add(area)
        price = row.get("price")
        if price is not None and price != "":
            try:
                p = float(price)
                if p > 0:
                    price_vals.append(p)
                else:
                    price_undisclosed += 1
            except (ValueError, TypeError):
                price_undisclosed += 1
        else:
            price_undisclosed += 1

    total = len(listings)
    sources_list = []
    for src_name, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        pct = round(count / total * 100, 1) if total > 0 else 0
        sources_list.append({
            "id": src_name.lower().replace(" ", "_").replace("/", "_"),
            "name": src_name,
            "count": count,
            "percentage": pct,
            "category": "live_supabase_data",
            "connection": "Supabase market_listings",
            "status": "connected",
        })

    price_disclosed = len(price_vals)
    avg_price = round(sum(price_vals) / len(price_vals)) if price_vals else 0
    max_price = int(max(price_vals)) if price_vals else 0
    min_price = int(min(price_vals)) if price_vals else 0

    return {
        "total_listings": total,
        "governorates_covered": len(gov_set),
        "unique_areas": len(area_set),
        "price_disclosed": price_disclosed,
        "price_undisclosed": price_undisclosed,
        "price_disclosure_pct": round(price_disclosed / total * 100, 1) if total > 0 else 0,
        "price_undisclosed_pct": round(price_undisclosed / total * 100, 1) if total > 0 else 0,
        "average_price": avg_price,
        "highest_price": max_price,
        "lowest_price": min_price,
        "sources_count": len(sources_list),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }, sources_list


def main():
    print("=" * 60)
    print("INCREMENTAL SUPABASE SYNC — alforaijboard")
    print("=" * 60)

    # 1. Fetch listings
    print("\n1. Fetching listings...")
    listings = fetch_incremental_listings()
    print(f"   Total: {len(listings)}")

    # 2. Fetch developments
    print("\n2. Fetching market_developments...")
    developments = fetch_developments()
    print(f"   Total: {len(developments)}")

    # 3. Compute statistics
    print("\n3. Computing statistics...")
    analysis, sources_list = compute_statistics(listings)
    print(f"   Sources: {len(sources_list)}")

    # 4. Save files
    print("\n4. Saving JSON files...")

    with open(os.path.join(OUT_DIR, "market_listings.json"), "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"   OK market_listings.json ({len(listings)} rows)")

    with open(os.path.join(OUT_DIR, "market_developments.json"), "w", encoding="utf-8") as f:
        json.dump(developments, f, ensure_ascii=False, indent=2)
    print(f"   OK market_developments.json ({len(developments)} rows)")

    with open(os.path.join(OUT_DIR, "sources.json"), "w", encoding="utf-8") as f:
        json.dump(sources_list, f, ensure_ascii=False, indent=2)
    print(f"   OK sources.json ({len(sources_list)} sources)")

    with open(os.path.join(OUT_DIR, "analysis.json"), "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"   OK analysis.json updated")

    # 5. Save sync marker
    if listings:
        latest_ts = None
        for row in listings:
            ts = row.get("updated_at") or row.get("created_at")
            if ts:
                if latest_ts is None or ts > latest_ts:
                    latest_ts = ts
        if latest_ts:
            save_sync_marker(latest_ts)
            print(f"\n5. Sync marker saved: {latest_ts}")
        else:
            print("\n5. No timestamp found — marker not saved")

    # 6. Summary
    print("\n" + "=" * 60)
    print("DONE — Incremental Sync Complete")
    print("=" * 60)
    print(f"Total listings: {analysis['total_listings']}")
    print(f"Sources: {analysis['sources_count']}")
    print(f"Developments: {len(developments)}")
    print(f"Governorates: {analysis['governorates_covered']}")
    print(f"Areas: {analysis['unique_areas']}")
    print(f"Price disclosed: {analysis['price_disclosed']} ({analysis['price_disclosure_pct']}%)")
    print(f"Price undisclosed: {analysis['price_undisclosed']} ({analysis['price_undisclosed_pct']}%)")
    print(f"Average price: {analysis['average_price']:,} KD")
    print(f"Highest price: {analysis['highest_price']:,} KD")


if __name__ == "__main__":
    main()
