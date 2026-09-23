#!/usr/bin/env python3
"""health_schema_test_2.py — Supabase schema dump."""
import urllib.request, json
url="https://bwspcsiazbwrrxpgoldx.supabase.co/rest/v1/cron_results?limit=1"
hdr={"apikey":"sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ","Authorization":"Bearer sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ","Content-Type":"application/json"}
req=urllib.request.Request(url, headers=hdr)
with urllib.request.urlopen(req, timeout=30) as r:
    data=json.loads(r.read().decode())
    print("COLS:", list(data[0].keys()))
