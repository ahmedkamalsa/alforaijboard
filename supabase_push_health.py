#!/usr/bin/env python3
"""Supabase health push — apikey-only, no auth header. Standalone."""
from __future__ import annotations
import os, json, datetime, urllib.request, urllib.error
from pathlib import Path

PROJECT_ID  = "bwspcsiazbwrrxpgoldx"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
API_KEY_ENV = "SUPABASE_ANON_KEY"
R = Path(r"C:/Users/hello/alforaijboard-gh")
HIST_FILE = R / "cron_results_local.json"
API_HEADERS = {"Content-Type": "application/json", "Prefer": "return=minimal"}

def get_key():
    k = os.environ.get(API_KEY_ENV) or ""
    if k:
        return k
    dotenv = R / ".env"
    if dotenv.exists():
        for line in dotenv.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("SUPABASE_ANON_KEY="):
                return s.split("=",1)[1].strip().strip('"').strip("'")
    return ""

def push(report):
    key = get_key()
    if not key:
        print("[Supabase push SKIP] no API key", flush=True)
        return False
    body = json.dumps({"report": report}).encode("utf-8")
    headers = {**API_HEADERS, "apikey": key, "Authorization": f"Bearer {key}"}
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/cron_results",
        data=body, headers=headers, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            print(f"[Supabase push OK] HTTP {resp.status}", flush=True)
            return True
    except urllib.error.HTTPError as he:
        msg = he.read().decode("utf-8", "replace")
        print(f"[Supabase push HTTP {he.code}] {he.reason} :: {msg[:300]}", flush=True)
        return False
    except Exception as e:
        print(f"[Supabase push ERR] {e}", flush=True)
        return False

if __name__ == "__main__":
    report_path = R / "cron_results" / "latest_health.json"
    if not report_path.exists():
        print("[No report] latest_health.json missing", flush=True)
        raise SystemExit(1)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    ok = push(report)
    # update local history with db_status
    hist = []
    if HIST_FILE.exists():
        hist = json.loads(HIST_FILE.read_text(encoding="utf-8"))
    if hist:
        hist[-1]["db_status"] = "PUSHED" if ok else "PUSH_FAILED"
        HIST_FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(0 if ok else 1)
